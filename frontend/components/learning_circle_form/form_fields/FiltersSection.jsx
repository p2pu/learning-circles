import React, { Component } from 'react'
import Filter from './Filter'
import FilterForm from './FilterForm'

export default class FilterSection extends Component {
  constructor(props) {
    super(props)
    this.state = { activeFilter: '' };
    this.updateActiveFilter = (filter) => this._updateActiveFilter(filter);
  }

  _updateActiveFilter(filter) {
    this.setState({ activeFilter: filter })
  }

  render() {
    return(
      <div className="filter-section">
        <div className='label'>
          Filter
        </div>
        <div className='filters-bar'>
          {
            this.props.filterCollection.map((filter, index) => {
              const isActive = this.state.activeFilter === filter;
              return(
                <div key={index} className='wrapper'>
                  <Filter
                    filter={filter}
                    active={isActive}
                    updateActiveFilter={this.updateActiveFilter}
                  />
                  {
                    isActive &&
                    <FilterForm
                      activeFilter={this.state.activeFilter}
                      updateActiveFilter={this.updateActiveFilter}
                      {...this.props}
                    />
                  }
                </div>
              )
            })
          }
        </div>
      </div>
    )
  }
}
