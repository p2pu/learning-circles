import React from 'react'


export const Step1 = () => (
  <div className='help-text'>
    <h4>Course selection tips</h4>
    <div className='content'>
      <p>The courses here were added by past facilitators. By default, courses list alphabetically but you can also order by the number of times each course has been used. We try to keep this list limited to on-demand courses, but you should confirm that a course is available by clicking “see the course” before you select it.</p>
      <p>For more information on how to select a good course, <a href="https://community.p2pu.org/t/what-to-look-for-in-a-course/2756" target="_blank" rel="noopener noreferrer">check out this discussion thread on the community.</a></p>
      <p>If you want to use a course that is not listed on the P2PU courses page, that is fine too! You can use any course from around the web so long as it is free for learners. <a href="https://community.p2pu.org/t/how-do-i-find-a-good-online-course/2757" target="_blank" rel="noopener noreferrer">You can learn more about searching for online courses on the community</a>, as well. Once you find a course you like, you can add that here.</p>
      <a href="/en/course/create/"><button className="p2pu-btn blue">add a course</button></a>
    </div>
  </div>
)


export const Step2 = () => (
  <div className='help-text'>
    <h4>How to choose a good location</h4>
    <div className='content'>
      <p>Learning circle location checklist:</p>
      <ul>
        <li>Available each week</li>
        <li>Easily accessible space</li>
        <li>Consistent access to power and internet</li>
        <li>Modular seating arrangements</li>
        <li>Accommodates physical and/or learning disabilities</li>
        <li>Restroom availability</li>
        <li>A large wall for projecting on</li>
        <li>Natural light</li>
        <li>Near public transport / free parking</li>
      </ul>
      <p>Other considerations:</p>
      <ul>
        <li>Do you need to book this location in advance?</li>
        <li>Do you have access to any keys that you need?</li>
        <li>Do you know the wifi network name and password?</li>
        <li>Do you know where chairs, tables, and additional supplies are stored?</li>
        <li>Are you aware of any rules determining what time you must finish by each week?</li>
      </ul>
      <p>For more information, check out the <a href="https://community.p2pu.org/t/how-to-choose-a-good-location-for-learning-circles/2758" target="_blank" rel="noopener noreferrer">“How to choose a good location for learning circles”</a> discussion thread.</p>
    </div>
  </div>
)

export const Step3 = () => (
  <div className='help-text'>
    <h4>When should we meet?</h4>
    <div className='content'>
      <ul>
        <li>Six weeks for 90-120 minutes each week is a good default learning circle length. It’s long enough that folks will get to know each other and have time to make noticeable improvements in their skills, but not so long that it is an overwhelming commitment.</li>
        <li>You should allow at least four weeks for promoting your learning circle.</li>
        <li>By default, the learning circle will be at the same time each week. If you need to change a specific meeting time, you can do that from within your learning circle dashboard.</li>
      </ul>
    </div>
  </div>
)


export const Step4 = () => (
  <div className='help-text'>
    <h4>Add the finishing touches</h4>
    <div className='content'>
      <ul>
        <li>In the welcome message, include something about yourself, why you’re facilitating this learning circle, or anything else you want people to know when they sign up.</li>
        <li>Make your learning circle stand out by uploading a picture or a .gif. It could be related to the location, subject matter, or anything else you want to identify your learning circle with!</li>
        <li>This is an example of how your custom content will be used on the sign up form: <br />
          <img src='/static/images/signup-form-screenshot.png' alt='Learning circle sign up form'/>
        </li>
      </ul>
    </div>
  </div>
)

export const Step5 = () => (
  <div className='help-text'>
    <h4>This is between us</h4>
    <div className='content'>
      <ul>
        <li>This information won’t be visible to learning circle participants. We will share it with a group of P2PU staff and veteran facilitators who can give you feedback and help you prepare for your learning circle.</li>
        <li>When you are finished, click 'PUBLISH'. If you don’t want your learning circle to go live yet, click 'SAVE & PUBLISH LATER'. You can then publish your learning circle from your dashboard whenever you are ready to start promoting.</li>
      </ul>
    </div>
  </div>
)