import Tabs from 'react-bootstrap/Tabs';
import Tab from 'react-bootstrap/Tab';

import File from './components/File';
import Cameras from './components/Cameras';
import Arduino from './components/Arduino';


export default function App(){

  return (
    <Tabs defaultActiveKey="profile" id="uncontrolled-tab-example">
      <Tab eventKey='runTab' title="File">
        <File/>
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
