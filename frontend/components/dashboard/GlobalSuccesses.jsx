import React, { Component } from "react";
import ApiHelper from "../../helpers/ApiHelper";
import AOS from 'aos';
import { DEFAULT_LC_IMAGE } from "../../helpers/constants"

const PAGE_LIMIT = 3;
const TOTAL_LIMIT = 9;


export default class GlobalSuccesses extends Component {
  constructor(props) {
    super(props);
    this.state = {
      items: [],
      errors: [],
      limit: PAGE_LIMIT,
      offset: 0,
    };
  }

  componentDidMount() {
    this.populateResources();
    AOS.init();
  }

  componentDidUpdate() {
    AOS.refresh();
  }

  populateResources = (params={}) => {
    const api = new ApiHelper('learningCircleSuccesses');

    const onSuccess = (data) => {
      if (data.status && data.status === "error") {
        return this.setState({ errors: data.errors })
      }

      this.setState({ items: data.items,  offset: data.offset, limit: data.limit })
    }

    const defaultParams = { limit: this.state.limit, offset: this.state.offset }

    api.fetchResource({ callback: onSuccess, params: { ...defaultParams, ...params } })
  }

  nextPage = (e) => {
    e.preventDefault();
    const params = { limit: PAGE_LIMIT, offset: this.state.offset + this.state.items.length };
    this.populateResources(params)
  }

  prevPage = (e) => {
    e.preventDefault();
    const params = { limit: PAGE_LIMIT, offset: this.state.offset - PAGE_LIMIT };
    this.populateResources(params)
  }

  render() {
    const totalPages = Math.ceil(TOTAL_LIMIT / PAGE_LIMIT);
    const currentPage = Math.ceil((this.state.offset + this.state.items.length) / PAGE_LIMIT);

    if (this.state.errors.length > 0) {
      return(
        <div className="py-2">
          <div>{ this.state.errors }</div>
        </div>
      )
    };

    return (
      <div className="global-successes">
        {
          this.state.items.map((lc, index) => {
            const formattedCity = lc.city.replace(/United States of America/, 'USA');
            const delay = index * 100;
            const imageSrc = lc.image_url || DEFAULT_LC_IMAGE

            return(
              <div className="meeting-card py-3 row" key={lc.id} data-aos='fade-up' data-aos-delay={delay}>
                <div className="col-4 image-thumbnail">
                  <img src={imageSrc} />
                </div>

                <div className="content col-8">

                  <div className="info">
                    {
                      lc.signup_count &&
                      <p className='meeting-info my-1'><span className="bold">{lc.signup_count}</span> people participated in <span className="bold">{lc.name}</span> in { formattedCity }</p>
                    }
                    {
                      !lc.signup_count &&
                      <p className='meeting-info my-1'><span className="bold">{lc.name}</span> wrapped up in { formattedCity }</p>
                    }
                    <a href={lc.report_url}>See the final report</a>
                  </div>

                </div>
              </div>
            )
          })
        }
        {
          (this.state.items.length > 0 && totalPages > 1) &&
          <nav aria-label="Page navigation">
            <ul className="pagination">
              <li className={`page-item ${currentPage <= 1 ? 'disabled' : ''}`}>
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
      </div>
    );
  }
}
