const { Given, When, Then } = require("@cucumber/cucumber");
const { By, until } = require("selenium-webdriver");
const assert = require("assert");

Given(
  "que estou na página com a tabela principal usando um mouse",
  async function () {
    await this.driver.get(this.baseUrl);
  }
);

When(
  "eu passo o mouse sobre o link {string} usando um mouse",
  async function (linkText) {
    const link = await this.driver.wait(
      until.elementLocated(By.xpath(`//a[contains(text(), '${linkText}')]`)),
      5000
    );

    await this.driver.actions().move({ origin: link }).perform();
    await this.driver.sleep(2000); // Aguarda 2 segundos para o efeito de hover aparecer
  }
);

Then(
  "o background do link {string} deve ser {string} ou {string}",
  async function (linkText, expectedColor1, expectedColor2) {
    console.log(`Verificando o background do link: ${linkText}`);
    const link = await this.driver.wait(
      until.elementLocated(By.xpath(`//a[contains(text(), '${linkText}')]`)),
      5000
    );

    await this.driver.sleep(500);

    const backgroundColor = await link.getCssValue("background-color");

    console.log(`Cor de fundo obtida: ${backgroundColor}`);

    assert.ok(
      backgroundColor === expectedColor1 || backgroundColor === expectedColor2,
      `Esperado: ${expectedColor1} ou ${expectedColor2}, mas obteve: ${backgroundColor}`
    );
  }
);
