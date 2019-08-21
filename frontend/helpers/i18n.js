export function day(day_) {
  if (WEEK_DAYS.hasOwnProperty(day_)){
    return WEEK_DAYS[day_];
  }
  return day_;
};

export function date(date_){
  return date_;
}

/* takes time formatted as hh:mm:ss and outputs it without seconds in the locale format */
export function time(time_){
  let [h,m,s] = time_.split(':');
  let now = new Date();
  now.setHours(h);
  now.setMinutes(m);
  return now.toLocaleTimeString('default', {hour: 'numeric', minute:'2-digit'});
}

export function datetime(datetime_){
  return new Date(datetime_).toLocaleString('default', {
    day: 'numeric', weekday: 'short', month: 'short', year: 'numeric',
    hour: 'numeric', minute: '2-digit'
  });
}
