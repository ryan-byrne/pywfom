import { useState, useEffect } from 'react';

// Bootstrap Component
import Tabs from 'react-bootstrap/Tabs';
import Tab from 'react-bootstrap/Tab';
import Modal from 'react-bootstrap/Modal';

// Each Tab's Components
import File from './tabs/File/Main';
import Cameras from './tabs/Cameras/Main';
import Arduino from './tabs/Arduino/Main';

const StatusPage = (props) => {
  return (
    <div>{

      <Modal show={props.message ? true : false}>
          <Modal.Header>
            <Modal.Title>Status</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            {props.message}
          </Modal.Body>
      </Modal>

      }</div>
  )
}

export default function Main() {

  const [fileConfig, setFileConfig] = useState({})
  const [arduinoConfig, setArduinoConfig] = useState({})
  const [camerasConfig, setCamerasConfig] = useState({})

  const [status, setStatus] = useState(null);

  const loadConfiguration = () => {
    fetch('/api/configure')
      .then(resp => resp.json()
      .then(data => {
        setStatus("Getting Camera Configurations");
        Object.keys(data.devices).filter(key=>key!='arduino').map((key, idx)=>{
          const cam = data.devices[key];
          setCamerasConfig({...camerasConfig, [cam.id]:cam})
        });
        setStatus("Getting Arduino Configuration");
        setArduinoConfig(data.devices.arduino);
        setStatus("Getting File Configuration");
        setFileConfig(data.file);
        setStatus(null);
      }))
  }

  const loadFromFile = () => {

  }

  const saveToFile = () => {

  }

  useEffect(() => {
    loadConfiguration()
  },[])

  return (
    <div>
      <Tabs defaultActiveKey="profile" id="uncontrolled-tab-example">
        <Tab eventKey='runTab' title="Run">
          <File fileConfig={fileConfig} setFileConfig={setFileConfig}/>
        </Tab>
        <Tab eventKey='camerasTab' title="Cameras">
          <Cameras camerasConfig={camerasConfig} setCamerasConfig={setCamerasConfig}/>
        </Tab>
        <Tab eventKey='arduinoTab' title="Arduino">
          <Arduino arduinoConfig={arduinoConfig} setArduinoConfig={setArduinoConfig}/>
        </Tab>
      </Tabs>
      { status ? <StatusPage message={status}/> : null}
    </div>
  )
}
