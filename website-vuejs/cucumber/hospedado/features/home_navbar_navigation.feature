@navbar-navigation
Feature: Navegar para outras interfaces a partir da navbar e exibir dropdown de anos

  Scenario: Clicar em Sobre na navbar
    Given que estou na página inicial da navbar
    When clico no link "Sobre" na navbar
    Then sou direcionado para a URL da navbar "https://cuidando.vc/sobre"

  Scenario: Clicar em Aprenda+ na navbar
    Given que estou na página inicial da navbar
    When clico no link "Aprenda+" na navbar
    Then sou direcionado para a URL da navbar "https://cuidando.vc/glossario"

  Scenario: Clicar em Análises na navbar
    Given que estou na página inicial da navbar
    When clico no link "Análises" na navbar
    Then sou direcionado para a URL da navbar "https://cuidando.vc/analises"

  Scenario: Exibir lista de anos ao clicar no botão de ano
    Given que estou na página inicial da navbar
    When clico no botão de ano
    Then a lista de anos é exibida
