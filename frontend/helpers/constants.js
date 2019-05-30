export const LEARNING_CIRCLES_LIMIT = 11;
export const DESKTOP_BREAKPOINT = 768;

export const SEARCH_PROPS = {
  learningCircles: {
    filters: ['location', 'topics', 'meetingDays'],
    placeholder: 'Keyword, organization, facilitator, etc...',
  },
  courses: {
    filters: ['topics', 'orderCourses'],
    placeholder: 'Title, subject, etc...',
  }
};

export const SEARCH_SUBJECTS = {
  learningCircles: 'learning circles',
  courses: 'courses'
};

export const MEETING_DAYS = [
  'Monday',
  'Tuesday',
  'Wednesday',
  'Thursday',
  'Friday',
  'Saturday',
  'Sunday'
];

export const API_ENDPOINTS = {
  learningCircle: '/api/learning-circle/',
  registration: '/en/accounts/fe/register/',
  login: '/en/accounts/fe/login/',
  whoami: '/en/accounts/fe/whoami/',
  learningCircles: {
    postUrl: '/api/learning-circle/',
    baseUrl: '/api/learningcircles/?',
    searchParams: ['q', 'topics', 'weekdays', 'latitude', 'longitude', 'distance', 'active', 'limit', 'offset', 'city', 'signup', 'team_id', 'id', 'user', 'scope', 'draft']
  },
  courses: {
    baseUrl: '/api/courses/?',
    searchParams: ['q', 'topics', 'order', 'course_id', 'user', 'include_unlisted', 'limit', 'offset']
  },
  learningCirclesTopics: {
    baseUrl: '/api/learningcircles/topics/?',
    searchParams: []
  },
  coursesTopics: {
    baseUrl: '/api/courses/topics/?',
    searchParams: []
  },
  stats: {
    baseUrl: '/api/landing-page-stats/?',
    searchParams: []
  },
  landingPage: {
    baseUrl: '/api/landing-page-learning-circles/?',
    searchParams: ['team', 'scope']
  },
  images: {
    postUrl: '/api/upload_image/'
  },
  learningCircleSuccesses: {
    baseUrl: '/api/learningcircles/successes/?',
    searchParams: ['limit', 'offset']
  },
  instagram: {
    baseUrl: '/api/instagram-feed/?',
    searchParams: []
  }
};

// export const LC_PUBLISHED_PAGE = '/en/facilitator/study_group/published';
// export const LC_SAVED_DRAFT_PAGE = '/en/facilitator/study_group/saved';
export const FACILITATOR_PAGE = '/en/';

export const LC_DEFAULTS = {
  duration: 90,
  weeks: 6,
  course: {},
  draft: true,
  language: 'en',
};

export const FACILITATOR_SURVEY = 'wPg50i';
export const NO_STUDYGROUP_SURVEY = 'iVldef';
export const LEARNER_SURVEY = 'VA1aVz';

export const DISCOURSE_API_URL = 'https://community.p2pu.org';
export const FACILITATOR_RESOURCE_TYPES = [
  'video', 'activity', 'blog', 'template', 'thread'
]

