@about-main-navigation
Feature: Navegar para a notícia externa através do link "aqui" na seção "Sobre"

  Scenario: Clicar no link "aqui" para visualizar a notícia sobre a menção honrosa
    Given que estou na seção "Sobre"
    When clico no link "aqui" para ver a notícia da menção honrosa
    Then sou redirecionado para a URL externa "http://www5.each.usp.br/noticias/projeto-cuidando-do-meu-bairro-recebe-mencao-honrosa-no-premio-luiz-fernando-de-computacao/"
