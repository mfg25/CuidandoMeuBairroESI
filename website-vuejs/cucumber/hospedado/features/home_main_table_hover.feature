@home_main_table_hover
Feature: Verificar efeito de hover no link "Baixar Tabela"

  Scenario: O background do link "Baixar Tabela" muda ao passar o mouse
    Given que estou na página com a tabela principal usando um mouse
    When eu passo o mouse sobre o link "Baixar tabela" usando um mouse
    Then o background do link "Baixar tabela" deve ser "rgba(244, 78, 22, 1)" ou "rgba(246, 113, 70, 1)"
