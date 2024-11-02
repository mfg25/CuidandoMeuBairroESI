const { Given, When, Then, setDefaultTimeout } = require("@cucumber/cucumber");
const { By, until } = require("selenium-webdriver");
const assert = require("assert");

// Aumentando o tempo limite, visto que uma nova aba é aberta e demonstrou ser mais lenta
setDefaultTimeout(30000); // 30 segundos

Given('que estou na seção "Sobre"', async function () {
  await this.driver.get("https://cuidando.vc/sobre");
});

When(
  "clico no link {string} para ver a notícia da menção honrosa",
  async function (linkText) {
    const linkSelector = By.css(
      'a[href="http://www5.each.usp.br/noticias/projeto-cuidando-do-meu-bairro-recebe-mencao-honrosa-no-premio-luiz-fernando-de-computacao/"]'
    );

    await this.driver.wait(until.elementLocated(linkSelector), 15000);
    const link = await this.driver.findElement(linkSelector);
    await link.click();

    // Trocar para a nova aba
    const tabs = await this.driver.getAllWindowHandles();
    await this.driver.switchTo().window(tabs[1]);
  }
);

Then(
  "sou redirecionado para a URL externa {string}",
  async function (expectedUrl) {
    await this.driver.wait(until.urlIs(expectedUrl), 15000);

    const currentUrl = await this.driver.getCurrentUrl();
    assert.strictEqual(
      currentUrl,
      expectedUrl,
      `A URL atual é diferente da esperada. Atual: ${currentUrl}`
    );

    // Fechar a aba e voltar para a original
    await this.driver.close();
    const tabs = await this.driver.getAllWindowHandles();
    await this.driver.switchTo().window(tabs[0]);
  }
);
