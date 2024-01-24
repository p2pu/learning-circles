import React, {useState, useEffect} from 'react';
import ApiHelper from "../../helpers/ApiHelper";
import moment from "moment"; //TODO


const CourseTable = ({courses, totalPages}) => <>
  <div className="table-responsive d-none d-md-block" data-aos='fade'>
    <table className="table">
      <thead>
        <tr>
          <td>Title</td>
          <td>Provider</td>
          <td>Date Added</td>
          <td></td>
        </tr>
      </thead>
      <tbody>
        {
          courses.map(course => {
            const date = moment(course.created_at).format('MMM D, YYYY')
            const classes = course.unlisted ? 'bg-cream-dark' : '';

            return(
              <tr key={course.id} className={`${classes}`}>
                <td><a href={course.course_page_path}>{`${course.unlisted ? "[UNLISTED] " : ""}${course.title}`}</a></td>
                <td>{course.provider}</td>
                <td>{date}</td>
                <td><a href={course.course_edit_path} className="p2pu-btn btn btn-sm dark">edit</a></td>
              </tr>
            )
          })
        }
      </tbody>
    </table>
  </div>

  <div className="d-md-none">
    {
      courses.map((course, index) => {
        const date = moment(course.created_at).format('MMM D, YYYY')
        const classes = course.unlisted ? 'bg-cream-dark' : '';
        const delay = index * 100;

        return(
          <div className={`meeting-card p-2 ${classes}`} key={course.id} data-aos='fade-up' data-aos-delay={delay}>
            <a className="bold" href={course.course_page_path}>{`${course.unlisted ? "[UNLISTED] " : ""}${course.title}`}</a>

            <div className="d-flex">
              <div className="pr-2">
                <div className="bold">Provider</div>
                <div className="bold">Date Added</div>
              </div>

              <div className="flex-grow px-2">
                <div className="">{ course.provider }</div>
                <div className="">{ date }</div>
              </div>
            </div>

            <a href={ course.course_edit_path } className="p2pu-btn btn btn-sm dark m-0 my-2">edit</a>
          </div>
        )
      })
    }
  </div>

  {
    totalPages > 1 &&
    <nav aria-label="Page navigation">
      <ul className="pagination">
        <li className={`page-item ${currentPage == 1 ? 'disabled' : ''}`}>
          <a className="page-link" href="" aria-label="Previous" onClick={this.prevPage}>
            <span aria-hidden="true">&laquo;</span>
            <span className="sr-only">Previous</span>
          </a>
        </li>
        <li className="page-item">
          <span className="page-link disabled">{`Page ${currentPage} of ${totalPages}`}</span>
        </li>
        <li className={`page-item ${currentPage == totalPages ? 'disabled' : ''}`}>
          <a className="page-link" href="" aria-label="Next" onClick={this.nextPage}>
            <span aria-hidden="true">&raquo;</span>
            <span className="sr-only">Next</span>
          </a>
        </li>
      </ul>
    </nav>
  }

</>


const CourseList = props => {
  const {teamId} = props;
  const [courseList, setCourseList] = useState({courses: [], count: 0, offset:0, limit: 20});
  useEffect(() => {
    const api = new ApiHelper('courses');
    const onSuccess = (data) => {
      setCourseList({ 
        courses: data.items,
        count: data.count,
        offset: data.offset,
        limit: data.limit 
      })
    }
    const params = {
      limit: courseList.limit,
      offset: courseList.offset, 
      team: true, 
    }
    api.fetchResource({ callback: onSuccess, params })
  }, [])
  return (
    <>
      <CourseTable
        courses={courseList.courses}
        totalPages={1}
      />
      <div className="text-right">
        <a href={props.editTeamCourseListUrl}>Add courses</a>
      </div>
    </>
  );
}

export default CourseList;
