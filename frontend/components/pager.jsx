import React from 'react'

/** Renders paging links */
export default class Pager extends React.Component {
    constructor(props){
        super(props);
        [
            '_handleChange',
        ].forEach((method) => this[method] = this[method].bind(this));
    }

    _handleChange(page, e){
        e.preventDefault();
        const newPage = Math.max(Math.min(page, this.props.pages-1), 0);
        if (newPage != this.props.activePage){
            this.props.onChange(page);
        }
    }

    render(){
        const {activePage, pages} = this.props;
        let pageNodes = [];
        var makePageLink = i => (
            <li key={i} 
                className={'page-item' + (i==activePage?' active':'')}
                onClick={this._handleChange.bind(this,i)}>
                <a className='page-link' href='#'>{i+1}</a>
            </li>
        );

        pageNodes.push(
            <li key='prev'
                className={'page-item' + (activePage==0?' disabled':'')}
                onClick={this._handleChange.bind(this, activePage-1)}>
                <a className='page-link' href='#'>{gettext("Prev")}</a>
            </li>
        );

        let start = Math.max(Math.min(activePage-2, pages-7), 0);
        let end = Math.min(Math.max(6,start+4), pages-1);
        if (start != 0){
            pageNodes.push(makePageLink(0));
            if (start > 2){
                pageNodes.push(
                    <li key='p_' className='page-item disabled'><a className='page-link' href='#'>...</a></li>
                );
            } else {
                pageNodes.push(makePageLink(1));
            }
        }             
        for (let i=start; i<=end; ++i){
            pageNodes.push(makePageLink(i));
        }
        if (end != pages-1){
            if (end < pages - 3){
                pageNodes.push(
                    <li key='n_' className='page-item disabled'><a className='page-link' href='#'>...</a></li>
                );
            } else {
                pageNodes.push(makePageLink(pages-2));
            }
            pageNodes.push(makePageLink(pages-1));
        }

        pageNodes.push(
            <li key='next'
                className={'page-item' + (activePage==pages-1?' disabled':'')}
                onClick={this._handleChange.bind(this, activePage+1)}>
                <a className="page-link" href='#'>{gettext("Next")}</a>
            </li>
        );

        return (
            <nav aria-label="Page navigation">
              <ul className="pagination">{pageNodes}</ul>
            </nav>
        );
    }
}


Pager.propTypes = {
    activePage: React.PropTypes.number,
    pages: React.PropTypes.number,
    onChange: React.PropTypes.func
}
