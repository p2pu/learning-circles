import React, { Component } from "react";
import ApiHelper from "../../helpers/ApiHelper";

const PAGE_LIMIT = 5;

export default class GenericTable extends Component {
  constructor(props) {
    super(props);
    this.state = {
      items: [],
      limit: PAGE_LIMIT,
      count: 0
    };
  }

  componentDidMount() {
    this.populateResources();
  }

  populateResources = (params={}) => {
    const api = new ApiHelper('learningCircles');

    const onSuccess = (data) => {
      this.setState({ items: data.items, count: data.count, offset: data.offset, limit: data.limit })
    }

    const defaultParams = { limit: this.state.limit, offset: this.state.offset, user: true, draft: true, scope: "completed" }

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
    const totalPages = Math.ceil(this.state.count / PAGE_LIMIT);
    const currentPage = Math.ceil((this.state.offset + this.state.items.length) / PAGE_LIMIT);
    const { Table } = this.props;

    return (
      <div className="generic-table">
        <Table items={this.state.items} />
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
      </div>
    );
  }
}
