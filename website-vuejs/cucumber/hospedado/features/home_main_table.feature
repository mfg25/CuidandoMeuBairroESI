@home_main_table
Feature: Navegar para outras interfaces a partir da página principal

  Scenario: Clicar em Baixar Tabela
    Given que estou na tabela da página inicial
    When clico no link "Baixar tabela"
    Then sou direcionado para a URL "https://devcolab.each.usp.br/dadosorcamentarios/"
