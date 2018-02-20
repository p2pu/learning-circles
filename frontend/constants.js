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
  learningCircles: {
    postUrl: '/api/learning-circle/',
    baseUrl: '/api/learningcircles/?',
    searchParams: ['q', 'topics', 'weekdays', 'latitude', 'longitude', 'distance', 'active', 'limit', 'offset', 'city', 'signup', 'team_id', 'id']
  },
  courses: {
    baseUrl: '/api/courses/?',
    searchParams: ['q', 'topics', 'order', 'course_id']
  },
  learningCirclesTopics: {
    baseUrl: 'https://learningcircles.p2pu.org/api/learningcircles/topics/?',
    searchParams: []
  },
  coursesTopics: {
    baseUrl: 'https://learningcircles.p2pu.org/api/courses/topics/?',
    searchParams: []
  },
  stats: {
    baseUrl: 'https://learningcircles.p2pu.org/api/landing-page-stats/?',
    searchParams: []
  },
  landingPage: {
    baseUrl: 'https://learningcircles.p2pu.org/api/landing-page-learning-circles/?',
    searchParams: []
  },
  images: {
    postUrl: '/api/upload_image/'
  }
};

export const LC_PUBLISHED_PAGE = '/en/facilitator/study_group/published';
export const LC_SAVED_DRAFT_PAGE = '/en/facilitator/study_group/saved';
export const FACILITATOR_PAGE = '/en/facilitator';

export const LC_DEFAULTS = {
  duration: 90,
  weeks: 6,
  course: {}
};

export const EXTERNAL_APIS = {
  algolia: 'https://places-dsn.algolia.net/1/places',
  geonames: 'https://secure.geonames.org'
};

export const KANSAS_CITY_OPTION = {
  label: 'Kansas City, Missouri, United States of America',
  value: {
    administrative: ['Missouri'],
    country: {
      default: 'United States of America'
    },
    locale_names: {
      default: ['Kansas City']
    },
    // from https://tools.wmflabs.org
    _geoloc: {
      lat: 39.099722,
      lng: -94.578333
    }
  }
};

