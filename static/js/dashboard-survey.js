function dashboardSurvey(){
  return `
    <style>
      #deprecated-site-alert {
        transition: all 0.3s ease-in-out;
        bottom: -100px;
        opacity: 0;
        position: fixed;
        right: 0;
        left: 0;
        padding: 40px;
        z-index: 1000;
        display: flex;
        justify-content: center;
      }

      #deprecated-site-alert > div[role="alert"] {
        padding: 10px 20px;
        background: #049487;
        color: #fff;
        box-shadow: -2px 2px 8px 1px rgba(0,0,0,0.2);
        border: 2px solid #fff;
        border-radius: 8px;
        display: flex;
      }

      #deprecated-site-alert.showDeprecationAlert {
        bottom: 0;
        opacity: 1;
      }

      #deprecated-alert-close {
        background: transparent;
        border: none;
        color: rgba(255,255,255,0.7);
        margin-left: 6px;
      }
    </style>

    <div id="deprecated-site-alert" aria-hidden="true">
      <div role="alert" tabindex="1">
        <div class="text-center">
          <p>We're designing a new Facilitator Dashboard and we need your feedback! Are there any changes you'd like to see?</p>
          <div>
            <a href="https://p2pu.typeform.com/to/weIA87" id="go-to-survey" class="p2pu-btn btn-sm light" target="_blank" rel="noopener noreferrer">Yes!</a>
            <button id="go-away" class="p2pu-btn btn-sm light transparent">No, leave me alone.</button>
          </div>
        </div>
        <div>
          <button id="deprecated-alert-close" aria-label="Close">&times;</button>
        </div>
      </div>
    </div>

  `;
}

var callback = function(){
  // Handler when the DOM is fully loaded
  let body = document.getElementsByTagName('body')[0];
  body.insertAdjacentHTML("afterbegin", dashboardSurvey());

  var deprecationAlert = document.getElementById('deprecated-site-alert');
  var deprecationAlertCloseButton = document.getElementById('deprecated-alert-close');
  var goAwayButton = document.getElementById('go-away');
  var goToSurveyButton = document.getElementById('go-to-survey');
  var preventAlert = window.localStorage.getItem('prevent-survey-alert') === 'true';

  function showDeprecationAlert(alert) {
    alert.classList.add('showDeprecationAlert')
    alert.setAttribute('aria-hidden', 'false')
  }

  function hideDeprecationAlert(alert) {
    alert.classList.remove('showDeprecationAlert')
    alert.setAttribute('aria-hidden', 'true')
  }

  function savePreferences() {
    window.localStorage.setItem('prevent-survey-alert', 'true');
  }

  if (!preventAlert) {
    setTimeout(function() {
      showDeprecationAlert(deprecationAlert);
    }, 2000);
  }

  deprecationAlertCloseButton.addEventListener('click', function() {
    hideDeprecationAlert(deprecationAlert);
  })

  goAwayButton.addEventListener('click', function() {
    hideDeprecationAlert(deprecationAlert);
    savePreferences(deprecationAlert)
  })

  goToSurveyButton.addEventListener('click', function() {
    hideDeprecationAlert(deprecationAlert);
    savePreferences(deprecationAlert);
  })

}

if (
    document.readyState === "complete" ||
    (document.readyState !== "loading" && !document.documentElement.doScroll)
) {
  callback();
} else {
  document.addEventListener("DOMContentLoaded", callback);
}
