@question_button_popup
Feature: Exibir pop-up ao clicar no botão "Quero perguntar"

  Scenario: Usuário clica no botão "Quero perguntar" e um pop-up é exibido
    Given que estou na página inicial com o botão "Quero perguntar"
    When clico no botão "Quero perguntar"
    Then um pop-up é exibido na tela
