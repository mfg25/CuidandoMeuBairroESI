const { Given, When, Then } = require("@cucumber/cucumber");
const { By } = require("selenium-webdriver");
const assert = require("assert");

Given("que estou na página inicial da navbar", async function () {
  await this.driver.get(this.baseUrl);
});

When("clico no link {string} na navbar", async function (linkName) {
  const linkMap = {
    Sobre: "/sobre",
    "Aprenda+": "/glossario",
    Análises: "/analises",
  };

  const link = await this.driver.findElement(
    By.css(`a[href="${linkMap[linkName]}"]`)
  );
  await link.click();
});

Then(
  "sou direcionado para a URL da navbar {string}",
  async function (expectedUrl) {
    await this.driver.wait(() => {
      return this.driver.getCurrentUrl().then((url) => {
        return url === expectedUrl;
      });
    }, 15000);

    const currentUrl = await this.driver.getCurrentUrl();
    assert.strictEqual(currentUrl, expectedUrl);
  }
);
