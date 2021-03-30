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
import Login from './Login';

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
  const [loggedIn, setLoggedIn] = useState(false);

  return (
    <div>
      {
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
