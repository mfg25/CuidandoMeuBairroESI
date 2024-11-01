@navbar-navigation
Feature: Navegar para outras interfaces a partir da navbar

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
