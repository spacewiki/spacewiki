import React from 'react';
import { shallow } from 'enzyme';
import Browser from '../components/Browser';
import GhostViewer from '../components/GhostViewer';
import ErrorPage from '../components/ErrorPage';
import { Identity, Page } from '../Model';
import API from '../API';

jest.mock('whatwg-fetch');

test('UI States', () => {
  const user = new Identity();
  const route = {splat: '/'}
  const rev = new Page().latestRevision;
  const browser = shallow(
    <Browser route={route} initialUser={user}>
      <p></p>
    </Browser>
  );
  browser.setState({currentRevision: undefined});
  expect(browser.find(GhostViewer).length).toBe(1);
  expect(browser.find(ErrorPage).length).toBe(0);

  browser.setState({currentRevision: rev});
  expect(browser.find(GhostViewer).length).toBe(0);
  expect(browser.find(ErrorPage).length).toBe(0);

  browser.setState({currentRevision: undefined, error: new Error('Test')});
  expect(browser.find(GhostViewer).length).toBe(0);
  expect(browser.find(ErrorPage).length).toBe(1);
});
