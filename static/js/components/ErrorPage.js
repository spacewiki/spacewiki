import React, { Component } from 'react';

export default class ErrorPage extends Component {
  render() {
    return (
      <div>
        <main className="row">
          <div className="small-12 columns content">
            <h1>Oh No!</h1>
            <p>Something went wrong!</p>
            <p>{this.props.message}</p>
          </div>
        </main>
      </div>
    );
  }
}
