const { Given, When, Then } = require("@cucumber/cucumber");
const { By } = require("selenium-webdriver");
const assert = require("assert");

Given('que estou na página inicial', async function () {
  await this.driver.get(this.baseUrl); 
});

When('clico no link {string} na navbar', async function (linkName) {
  const linkMap = {
    'Sobre': '/sobre',
    'Aprenda+': '/glossario',
    'Análises': '/analises' 
  };

  const link = await this.driver.findElement(By.css(`a[href="${linkMap[linkName]}"]`)); 
  await link.click();
});

Then('sou direcionado para a URL {string}', async function (expectedUrl) {
  // Esperar que a URL mude antes de verificar
  await this.driver.wait(() => {
    return this.driver.getCurrentUrl().then(url => {
      return url === expectedUrl;
    });
  }, 7000); // Espera até 7 segundos pela URL correta
  
  const currentUrl = await this.driver.getCurrentUrl();
  assert.strictEqual(currentUrl, expectedUrl);
});
