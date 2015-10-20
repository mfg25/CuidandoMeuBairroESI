# coding: utf-8
from __future__ import print_function

import collections
import logging
import os
import string
import time

import arrow
import bs4
import dateutil.parser
import flask
import internetarchive
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.exc import NoResultFound

from esiclivre import models, extensions


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
VALID_ATTACHMENTS_NAME_CHARS = string.lowercase + string.digits + '.-_'


def parse_date(text):
    return arrow.get(dateutil.parser.parse(text, dayfirst=True))


class ParsedPedido(object):

    def __init__(self, raw_data, browser):

        self._browser = browser
        self._raw_data = raw_data
        self._main_data = self._get_main_data()

        if self._main_data:
            self._details = self._get_details()
            self.attachments = self._get_attachments()
            self.situation = self._get_situation()
            self.request_date = self._get_request_date()
            self.history = self._get_history()

    def _get_main_data(self):
        return self._raw_data.form

    def _get_details(self):
        return self._main_data.select('#ctl00_MainContent_dtv_pedido')[0]

    @property
    def protocol(self):
        data = self._details.tbody.select('tr')[0]
        _, protocol = data.select('td')
        return int(protocol.text.strip())

    @property
    def interessado(self):
        data = self._details.tbody.select('tr')[1]
        _, interessado = data.select('td')
        return interessado.text.strip()

    def _get_request_date(self):
        data = self._details.tbody.select('tr')[2]
        _, opened_at = data.select('td')
        # return dateutil.parser.parse(opened_at.text.strip(), dayfirst=True)
        return parse_date(opened_at.text.strip())

    @property
    def orgao(self):
        data = self._details.tbody.select('tr')[3]
        _, orgao = data.select('td')
        return orgao.text.strip()

    @property
    def contact_option(self):
        data = self._details.tbody.select('tr')[4]
        _, option = data.select('td')
        return option.text.strip()

    @property
    def description(self):
        data = self._details.tbody.select('tr')[5]
        _, desc = data.select('td')
        return desc.text.strip()

    def _get_attachments(self):
        grid = self._main_data.select(
            '#ctl00_MainContent_grid_anexos_resposta')

        if not grid:
            return ()  # 'Sem anexos.'
        else:
            grid = grid[0]

        data = grid.tbody.select('tr')[1:]
        if not data or not any([i.text.split() for i in data]):
            return ()  # 'Sem anexos.'

        result = ()
        for item in data:

            filename, created_at, fileid = item.select('td')

            attachment = collections.namedtuple(
                'PedidoAttachment', ['filename', 'created_at'])
            attachment.filename = clear_attachment_name(filename.text)
            # attachment.created_at = dateutil.parser.parse(
            #     created_at.text.strip(), dayfirst=True)
            attachment.created_at = parse_date(created_at.text.strip())

            upload_attachment_to_internet_archive(
                self.protocol, attachment.filename
            )

            print("anexo")
            print(attachment.filename)
            result += (attachment,)
        return result

    def _get_situation(self):
        fieldset = self._main_data.select('#fildSetSituacao')[0]
        data = fieldset.tbody.select('tr')[0]
        _, situation = data.select('td')[:2]
        return situation.text.strip()

    def _get_history(self):

        grid = self._main_data.select('#ctl00_MainContent_grid_historico')[0]

        # get the 2th to skip header...
        data = grid.tbody.select('tr')[1:]

        result = ()
        for item in data:
            situation, justification, responsible = item.select('td')[1:]
            date = item.span

            history = collections.namedtuple(
                'PedidoHistory',
                ['situation', 'justification', 'responsible', 'date']
            )
            history.situation = situation.text.strip()
            history.justification = justification.text.strip()
            history.responsible = responsible.text.strip()
            history.date = parse_date(date.text.strip())

            result += (history,)

        try:
            result = sorted(result, key=lambda h: h.date)
        except:
            pass

        return result


class Pedidos(object):

    _parsedpedidos = []
    _pedido_pagesource = []

    def set_full_data(self, browser):
        self._full_data = browser.navegador.find_element_by_id(
            'ctl00_MainContent_grid_pedido')

    def get_all_pages_source(self, browser):

        total_of_pedidos = len(self._full_data.find_elements_by_tag_name('a'))
        for pos in range(total_of_pedidos):

            self.set_full_data(browser)
            self._full_data.find_elements_by_tag_name('a')[pos].click()

            pagesource = bs4.BeautifulSoup(browser.navegador.page_source,
                                           "html5lib")

            self._pedido_pagesource.append(pagesource)

            if not pagesource.select('#ctl00_MainContent_grid_anexos_resposta'):  # noqa
                browser.navegador.back()
                continue
            else:
                # a ideia era baixar os anexo apenas durante o processo de
                # parsear o codigo fonte, mas ainda estou com dificuldades
                # para fazer uma requisição valida para o servidor sem usar o
                # selenium. Em um proximo refactoring esse processo pode ser
                # feito em durante o parsing do page source, background ou não.
                attachments = browser.navegador.find_element_by_id(
                    'ctl00_MainContent_grid_anexos_resposta'
                )
                if attachments:
                    self.get_pedido_attachments(attachments)

            browser.navegador.back()
        fix_attachment_name_and_extension()

    def get_pedido_attachments(self, attachments):

        for attachment in attachments.find_elements_by_tag_name('input'):

            # baixar o arquivo
            # TODO: Ignorar arquivos que já existem? Como lidar com a
            # atualização de um anexo?
            attachment.click()

            # a ideia aqui é que se houver algum arquivo .part, ou seja, algum
            # download ainda não terminou, o processo aguarde até esses
            # arquivos serem baixados ou completar N tentativas

            max_retries = 0
            if '.part' in os.listdir(flask.current_app.config['DOWNLOADS_PATH']):  # noqa
                print("Existe algum download inacabado...")
                while max_retries != 10:

                    download_dir = os.listdir(
                        flask.current_app.config['DOWNLOADS_PATH']
                    )

                    uncomplete_download = next(
                        (arq for arq in download_dir if arq.endswith('.part')),
                        None
                    )

                    if not uncomplete_download:
                        print("Sem downloads inacabados...")
                        break
                    else:
                        print("Aguardar 1 segundo...")
                        time.sleep(1)
                        max_retries += 1

    def process_pedidos(self, browser, page_source=None):

        # Existe a possibilidade da pagina não retornar um codigo fonte válido
        # a classe que estrutura o pedido retornará None se o código
        # fonte não for válido...
        if page_source:
            pedido = ParsedPedido(page_source, browser)
            self._parsedpedidos.append(pedido) if pedido else None
        else:
            self._parsedpedidos = list(p for p in (
                ParsedPedido(pp, browser) for pp in self._pedido_pagesource
                ) if p._main_data
            )

        return self._parsedpedidos

    def get_all_parsed_pedidos(self):
        return self._parsedpedidos


def clear_attachment_name(name):

    name = name.strip().lower()

    return ''.join([l for l in name if l in VALID_ATTACHMENTS_NAME_CHARS])


def fix_attachment_name_and_extension():
    # remover caracter invalidos
    # mudar extensão para lowercase
    # apagar arquivos .part (nessa etapa, se um arquivo ainda é .part é porque
    # o download falhou).
    download_dir = flask.current_app.config['DOWNLOADS_PATH']
    for _file in os.listdir(download_dir):

        print("file: {}".format(_file))

        _file_fullpath = '{}/{}'.format(download_dir, _file)

        if _file.endswith('.part'):
            os.remove(_file_fullpath)
        else:
            os.rename(
                _file_fullpath,
                '{}/{}'.format(download_dir, clear_attachment_name(_file))
            )


def update_pedido_messages(pre_pedido, pedido):
    '''Update messages for a pedido.'''
    new_insetion = False
    for item in pre_pedido.history:
        # Check if is a new msg
        already_inserted = False
        for itemDB in pedido.history:
            # justification can be empty, so using all fields
            if (item.date == itemDB.date and
               item.justification == itemDB.justification and
               item.situation == itemDB.situation and
               item.responsible == itemDB.responsible):
                already_inserted = True

        # Insert if is a new msg
        if not already_inserted:
            message = models.Message()
            message.date = item.date
            message.justification = item.justification
            message.responsible = item.responsible
            message.situation = item.situation
            message.pedido_id = pedido.id
            extensions.db.session.add(message)
            new_insetion = True

    extensions.db.session.commit() if new_insetion else None


def create_pedido_attachments(pre_pedido):

    attachments = []
    for item in pre_pedido.attachments:

        attachment = models.Attachment()
        attachment.created_at = item.created_at
        attachment.name = item.filename
        attachment.ia_url = u'https://archive.org/download/pedido_{}/{}'.format(
            pre_pedido.protocol, item.filename
        )

        extensions.db.session.add(attachment)
        attachments.append(attachment)
    extensions.db.session.commit() if attachments else None

    return attachments


def save_pedido_into_db(pre_pedido):
    # check if there is a object with the same protocol
    pedido = models.Pedido.query.filter(
        models.Pedido.protocol == pre_pedido.protocol)
    pedido = pedido.options(joinedload('history')).first()
    if not pedido:
        # if not, create one
        default_author = flask.current_app.config['DEFAULT_AUTHOR']
        try:
            author = extensions.db.session.query(models.Author).filter(
                models.Author.name == default_author
            ).one()
        except NoResultFound:
            author = models.Author(name=default_author)
            extensions.db.session.add(author)
            extensions.db.session.commit()

        pedido = models.Pedido(protocol=pre_pedido.protocol, author=author)
        pedido.add_keyword('recuperado')
        extensions.db.session.add(pedido)

    # TODO: O que fazer se o orgão não existir no DB?
    if not pre_pedido.orgao:
        orgao_name = 'desconhecido'
    else:
        orgao_name = pre_pedido.orgao

    orgao = models.Orgao.query.filter_by(name=orgao_name).first()
    if not orgao:
        orgao = models.Orgao(name=orgao_name)
        extensions.db.session.add(orgao)
        extensions.db.session.commit()
    pedido.orgao_name = orgao.name

    pedido.interessado = pre_pedido.interessado
    pedido.situation = pre_pedido.situation
    pedido.request_date = pre_pedido.request_date
    pedido.contact_option = pre_pedido.contact_option
    pedido.description = pre_pedido.description

    extensions.db.session.commit()

    update_pedido_messages(pre_pedido, pedido)

    if pre_pedido.attachments:
        pedido.attachments = create_pedido_attachments(pre_pedido)


def upload_attachment_to_internet_archive(pedido_protocol, filename):

    download_dir = flask.current_app.config['DOWNLOADS_PATH']
    downloaded_attachments = os.listdir(download_dir)

    if filename not in [a for a in downloaded_attachments]:
        print("Arquivo {!r} não existe!.".format(filename))
        # TODO: O que fazer se o arquivo não estiver disponivel?
        # Já temos um caso onde o download não completa, mas por falha no
        # servidor do esic.
        return None
    else:

        item = internetarchive.Item('pedido_{}'.format(pedido_protocol))
        metadata = dict(
            mediatype='pdf',
            creator='OKF',
            created_at=arrow.now().isoformat()
        )
        result = item.upload(
            '{}/{}'.format(download_dir, filename), metadata=metadata
        )

        if not result or result[0].status_code != 200:
            # TODO: O que fazer nessa situação?
            print("Erro ao executar upload.")
        else:
            os.remove('{}/{}'.format(download_dir, filename))


def update_pedidos_list(browser):

    # garantir que a tela inicial seja a de consulta de pedidos.
    browser.ir_para_consultar_pedido()

    pedidos = Pedidos()
    pedidos.set_full_data(browser)
    pedidos.get_all_pages_source(browser)
    pedidos.process_pedidos(browser)

    for pedido in pedidos.get_all_parsed_pedidos():
        save_pedido_into_db(pedido)

    # registrar atualização do dia
    extensions.db.session.add(
        models.PedidosUpdate(date=arrow.now())
    )
    extensions.db.session.commit()

    print("Pedidos atualizados. Atualização registrada.")
