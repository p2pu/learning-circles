import React from 'react'

export default class TabSelector extends React.Component {
    constructor(props){
        super(props);
        this.state = {
            activeTab: 0
        };
        this._handleTabSwitch = this._handleTabSwitch.bind(this); 
    }

    _handleTabSwitch(tabIndex, e){
        e.preventDefault();
        this.setState({activeTab: tabIndex});
    }

    render() {
        const {header, children} = this.props;
        const {activeTab} = this.state;
        var tabs = header.map((heading,i) =>
            <li role="presentation" key={i} className={i==activeTab&&'active'}>
                <a href="#" onClick={this._handleTabSwitch.bind(this,i)}>{heading}</a>
            </li>
        );
        var activeChild = React.Children.toArray(children)[activeTab];
        return (
            <div>
                <ul className="nav nav-pills nav-justified">{tabs}</ul>
                {activeChild}
            </div>
        );
    }
}
