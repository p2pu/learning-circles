const puppeteer = require('puppeteer');
const { expect } = require('chai');
let { browser, expect: expect_ } = global;
const globalVariables = Object.assign({}, { browser: browser, expect: expect_ });

// puppeteer options
const opts = {
  timeout: 10000
};

// expose variables
before (async function () {
  global.expect = expect;
  global.browser = await puppeteer.launch(opts);
});

// close browser and reset global variables
after (function () {
  global.browser.close();

  global.browser = globalVariables.browser;
  global.expect = globalVariables.expect;
});
