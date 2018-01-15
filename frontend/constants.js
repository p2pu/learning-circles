export const LEARNING_CIRCLES_LIMIT = 11;

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
}

export const MEETING_DAYS = [
  'Monday',
  'Tuesday',
  'Wednesday',
  'Thursday',
  'Friday',
  'Saturday',
  'Sunday'
]

export const API_ENDPOINTS = {
  learningCircles: {
    baseUrl: 'https://learningcircles.p2pu.org/api/learningcircles/?',
    searchParams: ['q', 'topics', 'weekdays', 'latitude', 'longitude', 'distance', 'active', 'limit', 'offset', 'city', 'signup', 'team_id']
  },
  courses: {
    baseUrl: 'https://learningcircles.p2pu.org/api/courses/?',
    searchParams: ['q', 'topics', 'order']
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
  }
}