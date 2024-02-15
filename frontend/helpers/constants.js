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
    searchParams: ['q', 'topics', 'order', 'course_id', 'user', 'include_unlisted', 'limit', 'offset', 'team']
  },
  learningCirclesTopics: {
    baseUrl: '/api/learningcircles/topics/?',
    searchParams: []
  },
  coursesTopics: {
    baseUrl: '/api/courses/topics/?',
    searchParams: []
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
  },
  teamMembers: {
    baseUrl: '/api/teams/members/?',
    searchParams: ['team_id', 'offset', 'limit']
  },
  teamInvitations: {
    baseUrl: '/api/teams/invitations/?',
    searchParams: ['team_id', 'offset', 'limit']
  },
  invitationNotifications: {
    baseUrl: '/api/facilitator/invitations/?',
    searchParams: []
  },
  announcements: {
    baseUrl: '/api/announcements/',
    searchParams: []
  }
};

export const FACILITATOR_PAGE = '/en/';

export const LC_DEFAULTS = {
  duration: 90,
  weeks: 6,
  course: {},
  online: false,
  draft: true,
  language: 'en',
  meetings: [],
};

// TODO - this needs to be configured, not baked into the code
export const NO_STUDYGROUP_SURVEY = 'iVldef';

export const DISCOURSE_API_URL = 'https://community.p2pu.org';
export const FACILITATOR_RESOURCE_TYPES = [
  'video', 'activity', 'blog', 'template', 'thread'
]

export const DEFAULT_LC_IMAGE = '/static/images/learning-circle-default.jpg'

