describe('learning circle creation', function () {
  let page;

  before (async function () {
    page = await browser.newPage();
    await page.setRequestInterception(true);
    await page.setCacheEnabled(false);

    page.on('request', request => {
      console.log(request.url());
      request.continue();
    });

    page.on('response', async response => {
      console.log(response.ok())
    });

    await page.goto('http://localhost:8000/en/studygroup/create/', {timeout: 0, waitUntil: ['networkidle0', 'load', 'domcontentloaded']});
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

  it('should show courses on the courses tab', async function() {
    let tab = await page.$('#react-tabs-1');
    let searchContainer = await page.$('.search-container')
    let resultsCards = await page.$$('.result-item', nodes => node)

    expect(await tab.$eval('h4', heading => heading.innerText)).to.equal('Step 1: Select a Course *');
    expect(searchContainer).to.not.be.null
    expect(resultsCards).to.have.lengthOf.above(0)



    // expect page to make call to api for courses, capture response
    // expect resultsCards to have the right number of results
  })

  it('should have a places selector on the location tab')
  // expect page to make external api call to algolia
  // expect field to be rendered

  describe('when the user is logged in', function() {
    before(async function() {
      // log in user
    })

    after(async function() {
      // delete user
    })

    it('should create a learning circle when filled out correctly and submitted')
    it('should save a learning circle as unpublished when filled out correctly and saved')
    it('should display errors if missing required fields')
  })

  describe('when the user is not logged in', function() {
    it('should show the user registration modal when the user clicks the submit button')
    it('should show the user registration modal when the user clicks the save button')
  })

  describe('registration modal', function() {
    it('should toggle between registration and log in form')
    it('should create a user when filled out correctly')
    it('should show errors when not filled out correctly')
    it('should log in the user when valid credentials are provided')
    it('should not log in the user if invalid credentials are provided')
  })

});


