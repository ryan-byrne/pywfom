import {useEffect, useState} from 'react';

import Container from 'react-bootstrap/Container';
import Button from 'react-bootstrap/Button';
import Table from 'react-bootstrap/Table';
import Alert from 'react-bootstrap/Alert';
import ButtonGroup from 'react-bootstrap/ButtonGroup';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';

import ViewRun from './ViewRun';

export default function Viewer(props){

  const [savedRuns, setSavedRuns] = useState([]);
  const [selected, setSelected] = useState(null);

  const handleFind = (user) => {
    fetch(`/api/db/runs/${user}`)
      .then(resp=>{
        if(resp.ok){ resp.json().then(data=>setSavedRuns(data))}
        else { resp.text().then(txt=>console.error(txt)) }
      })
  }

  return (
    <div>{
        selected !== null ? <ViewRun run={savedRuns[selected]} onLeave={()=>setSelected(null)}/> :
        <Container className="mt-3 justify-content-center">
          {
            savedRuns.length === 0 ? null :
            <Table striped bordered hover variant="dark" style={{cursor: "pointer"}}>
              <tbody>
                <tr><th>Date</th><th>Run By</th><th>Mouse</th><th>Run Length</th></tr>
                {
                  savedRuns.map((run,idx)=>(
                    <tr key={idx} onClick={()=>setSelected(idx)}>
                      <td>{run.date}</td>
                      <td>{run.user}</td>
                      <td>{run.mouse}</td>
                      <td>{run.config.file.run_length} {run.config.file.run_length_unit}</td>
                    </tr>
                  ))
                }
              </tbody>
            </Table>
          }
          <Row>
            <ButtonGroup as={Col} className="m-3">
              <Button onClick={()=>handleFind(props.user)}>My Runs</Button>
              <Button onClick={()=>handleFind("")} className="ml-3">All Runs</Button>
            </ButtonGroup>
          </Row>
        </Container>
      }</div>
  )
}
