describe('sample test', function () {
  let page;

  before (async function () {
    page = await browser.newPage();
    await page.goto('http://localhost:8000/en/accounts/register/');
  });

  after (async function () {
    await page.close();
  })

  it('should have the correct page title', async function () {
    expect(await page.title()).to.eql('Learning circles');
  });

  it('should have a form', async function () {
    let form = await page.$('form');

    expect(form).to.eql('Page Title');
  });

  it('should have 6 input fields', async function () {
    expect(await page.$$('input')).to.have.lengthOf(6);
  });

});

