function deprecatedAlert(){
  return `
    <style>
      #deprecated-site-alert {
        transition: all 0.3s ease-in-out;
        bottom: -100px;
        opacity: 0;
        position: fixed;
        right: 0;
        left: 0;
        padding: 20px;
        z-index: 1000;
        display: flex;
        justify-content: center;
      }

      #deprecated-site-alert > div[role="alert"] {
        padding: 20px;
        background: #FC7100;
        color: #fff;
        box-shadow: -2px 2px 8px 1px rgba(0,0,0,0.2);
        border: 2px solid #fff;
        border-radius: 8px;
        position: relative;
      }

      #deprecated-site-alert.showDeprecationAlert {
        bottom: 0;
        opacity: 1;
      }

      #deprecated-site-alert .close-btn {
        position: absolute;
        top: 4px;
        right: 4px;
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
          <p>The new Facilitator Dashboard is here! This page is deprecated and will soon be removed completely.</p>
          <div>
            <a href="/en/" id="go-to-dashboard" class="p2pu-btn btn-sm light">Go to the new dashboard</a>
          </div>
        </div>
      </div>
    </div>

  `;
}

var callback = function(){
  // Handler when the DOM is fully loaded
  let body = document.getElementsByTagName('body')[0];
  body.insertAdjacentHTML("afterbegin", deprecatedAlert());

  var deprecationAlert = document.getElementById('deprecated-site-alert');

  function showDeprecationAlert(alert) {
    alert.classList.add('showDeprecationAlert')
    alert.setAttribute('aria-hidden', 'false')
  }

  setTimeout(function() {
    showDeprecationAlert(deprecationAlert);
  }, 2000);

}

if (
    document.readyState === "complete" ||
    (document.readyState !== "loading" && !document.documentElement.doScroll)
) {
  callback();
} else {
  document.addEventListener("DOMContentLoaded", callback);
}
