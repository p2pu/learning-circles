describe('learning circle creation', function () {
  let page;

  before (async function () {
    page = await browser.newPage();
    await page.goto('http://learningcircles:8000/en/studygroup/create/', {timeout: 0, waitUntil: 'domcontentloaded'});
  });

  after (async function () {
    await page.close();
  })

  it('should have the correct page title', async function () {
    let title = await page.title();
    expect(title).to.eql('Learning circles');
  });

  it('creation dialog should show location selection', async function () {
    let tab = await page.$('#react-tabs-1');
    expect(await tab.$eval('h4', heading => heading.innerText)).to.equal('Step 1: Select a Course *');
  });

});

