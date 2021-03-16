import { useState, useEffect } from 'react';

// Bootstrap Component
import Tabs from 'react-bootstrap/Tabs';
import Tab from 'react-bootstrap/Tab';
import Modal from 'react-bootstrap/Modal';
import Alert from 'react-bootstrap/Alert';
import Button from 'react-bootstrap/Button';
import Spinner from 'react-bootstrap/Spinner';

// Each Tab's Components
import File from './tabs/File/Main';
import Cameras from './tabs/Cameras/Main';
import Arduino from './tabs/Arduino/Main';

const StatusPage = (props) => {

  return (
    <div>{
      <Modal className='h-100' show={props.message ? true : false}>
          <Alert variant={props.variant}>
            <Alert.Heading>
              {props.variant === 'danger' ? "ERROR:" :
                <div><Spinner animation="grow"></Spinner> Loading pyWFOM</div>
              }
            </Alert.Heading>
            <p>{props.message}</p>
              {
                props.variant !== 'danger'? null :
                <Button onClick={()=>window.location.reload()}>Refresh</Button>
              }
          </Alert>
      </Modal>
      }</div>
  )
}

export default function Main() {

  const [loading, setLoading] = useState({});
  const [settings, setSettings] = useState({})
  /*
  useEffect(()=>{
    setLoading({message:"Loading settings from Python API", variant:'info'})
    fetch('/api/settings')
      .then(resp=>resp.json()
      .then(data=>{
        const {arduino, file, ...cameras} = data;
        setSettings({arduino:arduino,file:file, cameras:cameras});
        setLoading({})
      })
      .catch(err=>{
        setLoading({message:"Unable to connect to server"})
      }))
  },[]);
  */

  return (
    <div>
      {
        loading.message ? <StatusPage message={loading.message} variant={loading.variant}/>:
        <Tabs defaultActiveKey="profile" id="uncontrolled-tab-example">
          <Tab eventKey='runTab' title="Run">
            <File />
          </Tab>
          <Tab eventKey='camerasTab' title="Cameras">
            <Cameras />
          </Tab>
          <Tab eventKey='arduinoTab' title="Arduino">
            <Arduino />
          </Tab>
        </Tabs>
      }
    </div>
  )
}
