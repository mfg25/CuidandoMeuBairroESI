const { Given, When, Then } = require("@cucumber/cucumber");
const { By, until } = require("selenium-webdriver");
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

When("clico no botão de ano", async function () {
  const button = await this.driver.findElement(
    By.css('button[data-dropdown-toggle="dropdownYear"]')
  );
  await button.click();
});

Then("a lista de anos é exibida", async function () {
  const dropdown = await this.driver.wait(
    until.elementLocated(By.css(".scroll-year-select")),
    5000
  );
  const isVisible = await dropdown.isDisplayed();
  assert.strictEqual(isVisible, true, "A lista de anos não foi exibida.");
});
