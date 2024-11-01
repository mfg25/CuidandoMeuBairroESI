Feature: Navegar para outras páginas a partir do menu de navegação na página inicial

  Scenario: Clicar em Sobre na navbar
    Given que estou na página inicial
    When clico no link "Sobre" na navbar
    Then sou direcionado para a URL "https://cuidando.vc/sobre"

  Scenario: Clicar em Aprenda+ na navbar
    Given que estou na página inicial
    When clico no link "Aprenda+" na navbar
    Then sou direcionado para a URL "https://cuidando.vc/glossario"
