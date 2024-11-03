const { Given, When, Then } = require("@cucumber/cucumber");
const { By } = require("selenium-webdriver");
const assert = require("assert");

Given("que estou na tabela da página inicial", async function () {
  await this.driver.get(this.baseUrl);
});

When("clico no link {string}", async function (linkName) {
  const link = await this.driver.findElement(
    By.xpath(`//a[contains(text(), '${linkName}')]`)
  );
  await link.click();
});

Then("sou direcionado para a URL {string}", async function (expectedUrl) {
  await this.driver.sleep(5000);

  // Muda para a nova aba
  const handles = await this.driver.getAllWindowHandles();
  await this.driver.switchTo().window(handles[handles.length - 1]);

  await this.driver.wait(() => {
    return this.driver.getCurrentUrl().then((url) => {
      return url === expectedUrl;
    });
  }, 15000);

  const currentUrl = await this.driver.getCurrentUrl();
  assert.strictEqual(currentUrl, expectedUrl);
});
