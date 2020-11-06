
// parses a 24 hour time string and return [hour, minute, seconds] as integers
export function parseTime(time){
  const [hour, minute, second='00'] = time.split(":");
  return [hour, minute,second].map(i => parseInt(i));
}

export function printTime(hour, minute, second=null){
  return `${hour}:` + `0${minute}`.substr(-2) + (second===null?'':':'+`0${second}`.substr(-2));
}
