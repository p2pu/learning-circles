describe('user signup', function () {
  let page;

  before (async function () {
    page = await browser.newPage();
    await page.goto('http://learningcircles:8000/en/accounts/register/', {timeout: 0, waitUntil: 'domcontentloaded'});
  });

  after (async function () {
    await page.close();
  })

  it('should have the correct page title', async function () {
    let title = await page.title();
    expect(title).to.eql('Learning circles');
  });


  it('signup form should have 8 input fields', async function () {
    let form = await page.$('form');
    expect(await form.$$('input')).to.have.lengthOf(8);
  });

});

