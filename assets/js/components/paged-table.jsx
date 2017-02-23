import React from 'react'
import Pager from './pager'

export default class PagedTable extends React.Component {
    constructor(props){
        super(props);
        this.state = {
            page: 0
        };
        this.handlePageChange = this.handlePageChange.bind(this);
    }

    pageCount(){
        return Math.max(1, Math.ceil(React.Children.count(this.props.children)/this.props.perPage));
    }

    handlePageChange(page){
        this.setState({page: page});
    }

    render(){
        let perPage = 10;
        let page = Math.min(this.pageCount()-1, this.state.page);
        let start = page*this.props.perPage;
        let end = start + this.props.perPage;
        let children = React.Children.toArray(this.props.children).slice(start, end);
        return (
            <div>
                <table>
                <thead>{this.props.heading}</thead>
                <tbody>{children}</tbody></table>
                <Pager 
                    pages={this.pageCount()} 
                    activePage={page} 
                    onChange={this.handlePageChange}/>
            </div>
        );
    }
}

PagedTable.propTypes = {
    perPage: React.PropTypes.number
}
