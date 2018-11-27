const DOMAIN = 'http://localhost:8000';

describe('learning circle creation', function () {
  let page;

  before (async function () {
    page = await browser.newPage();
    await page.setRequestInterception(true);
    await page.setCacheEnabled(false);

    pageRequests = []

    page.on('request', request => {
      console.log(request.url())
      request.continue();
    });

    page.on('response', async response => {
      pageRequests.push({ url: response.url(), response: response })
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

  it('should show courses on the courses tab', async function() {
    let tab = await page.$('#react-tabs-1');
    let searchContainer = await page.$('.search-container')
    let resultsCards = await page.$$('.result-item', nodes => node)
    const coursesApiRequest = pageRequests.find(response => response.url.includes(`${DOMAIN}/api/courses/?order=title`))

    expect(await tab.$eval('h4', heading => heading.innerText)).to.equal('Step 1: Select a Course *');
    expect(searchContainer).to.not.be.null
    expect(resultsCards).to.have.lengthOf.above(0)

    expect(coursesApiRequest).to.exist
    expect(coursesApiRequest.response.status()).to.eql(200)
  })

  it('should have a places selector on the location tab', async function() {
    await Promise.all([
      page.click("#react-tabs-2"),
      page.waitForResponse('https://places-dsn.algolia.net/1/places/query/'),
    ]);

    const placeSelectElement = await page.$(".city-select")
    const algoliaApiRequest = pageRequests.find(response => response.url.includes(`https://places-dsn.algolia.net/1/places/query/`))

    expect(placeSelectElement).to.exist
    expect(algoliaApiRequest).to.exist
    expect(algoliaApiRequest.response.status()).to.eql(200)
  })


  describe('when the user is not logged in', function() {
    it('should show the user registration modal when the user clicks the publish button', async function() {
      await page.click("#react-tabs-8")
      const publishButton = await page.$(".p2pu-btn.publish")
      await page.click(".p2pu-btn.publish")
      const registrationModal = await page.$(".registration-modal")

      expect(publishButton).to.exist
      expect(registrationModal).to.exist
    })

    it('should show the user registration modal when the user clicks the save button', async function() {
      await page.click("#react-tabs-8")
      const saveButton = await page.$(".p2pu-btn.save")
      await page.click(".p2pu-btn.save")
      const registrationModal = await page.$(".registration-modal")

      expect(saveButton).to.exist
      expect(registrationModal).to.exist
    })
  })

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

  describe('registration modal', function() {
    before(async function() {
      await page.click("#react-tabs-8")
      await page.$(".p2pu-btn.save")
      await page.click(".p2pu-btn.save")
      await page.$(".registration-modal")
    })

    it('should toggle between registration and log in form', async function() {
      expect(await page.$eval(".registration-modal-content h4", heading => heading.innerText)).to.equal("Create an account")
      expect(await page.$$(".registration-modal-content input")).to.have.lengthOf(5)

      await page.click(".modal-actions a")
      expect(await page.$eval(".registration-modal-content h4", heading => heading.innerText)).to.equal("Log in")
      expect(await page.$$(".registration-modal-content input")).to.have.lengthOf(2)

      await page.click(".modal-actions a")
      expect(await page.$eval(".registration-modal-content h4", heading => heading.innerText)).to.equal("Create an account")
      expect(await page.$$(".registration-modal-content input")).to.have.lengthOf(5)
    })

    it('should create a user when filled out correctly', async function() {
      page.type("#id_first_name", "Ted")
      page.type("#id_last_name", "Danson")
      page.type("#id_email", "teddy@mailinator.net")
      page.type("#id_password", "teddybear")

      await Promise.all([
        page.click(".registration-modal-content button[type='submit']"),
        // page.waitForResponse(`${DOMAIN}/en/accounts/fe/register/`),
      ]);

      console.log(pageRequests)

      await page.$(".alert-success")
      expect(await page.$eval(".alert-success .alert-content", alert => alert.innerText)).to.equal("You're logged in! You can now save or publish your learning circle.")
    })
    it('should show errors when not filled out correctly')
    it('should log in the user when valid credentials are provided')
    it('should not log in the user if invalid credentials are provided')
  })

});


