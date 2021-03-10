// Bootstrap Component
import Tabs from 'react-bootstrap/Tabs';
import Tab from 'react-bootstrap/Tab';

// Each Tab's Components
import File from './tabs//File/File';
import Cameras from './tabs/Cameras/Cameras';
import Arduino from './tabs/Arduino/Arduino';

export default function Main() {
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
