@home_main_table_hover
Feature: Verificar efeito de hover no link "Baixar Tabela"

  Scenario: O background do link "Baixar Tabela" muda ao passar o mouse
    Given que estou na página com a tabela principal
    When eu passo o mouse sobre o link "Baixar tabela"
    Then o background do link "Baixar tabela" deve ser "rgba(246, 113, 70, 1)"
