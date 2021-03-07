import Tabs from 'react-bootstrap/Tabs';
import Tab from 'react-bootstrap/Tab';

import Run from './components/Run';
import Cameras from './components/Cameras';
import Arduino from './components/Arduino';


export default function App(){

  return (
    <Tabs defaultActiveKey="profile" id="uncontrolled-tab-example">
      <Tab eventKey='runTab' title="Run">
        <Run/>
      </Tab>
      <Tab eventKey='camerasTab' title="Cameras">
        <Cameras/>
      </Tab>
      <Tab eventKey='arduinoTab' title="Arduino">
        <Arduino/>
      </Tab>
    </Tabs>
  )
}
