import Tabs from 'react-bootstrap/Tabs';
import Tab from 'react-bootstrap/Tab';

export default function Arduino(){
  return(
    <Tabs>
      <Tab eventKey='pinsTab' title="Pins">
      </Tab>
      <Tab eventKey='stimTab' title="Stim">
      </Tab>
      <Tab eventKey='firmwareTab' title="Firmware">
      </Tab>
    </Tabs>
  )
}
