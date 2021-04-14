import {useEffect, useState} from 'react';

import Container from 'react-bootstrap/Container';
import Button from 'react-bootstrap/Button';
import Table from 'react-bootstrap/Table';
import ButtonGroup from 'react-bootstrap/ButtonGroup';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';

export default function Viewer(props){

  const [runs, setRuns] = useState([]);
  const [viewing, setViewing] = useState(false);

  const handleSelect = (idx) => {
    console.log(runs[idx]);
  }

  const handleFind = (user) => {
    fetch(`/viewer/runs/${user}`)
      .then(resp=>{
        if(resp.ok){ resp.json().then(data=>{
          setRuns(data)
        })}
        else { resp.text().then(txt=>console.error(txt)) }
      })
  }

  return (
    <div>{
        viewing ? null :
      <Container className="mt-3 justify-content-center">
        {
          runs.length === 0 ? null :
          <Table striped bordered hover variant="dark" style={{cursor: "pointer"}}>
            <tbody>
              <tr><th>Date</th><th>Mouse</th><th>Run Length</th></tr>
              {
                runs.map((run,idx)=>(
                  <tr key={idx} onClick={()=>handleSelect(idx)}>
                    <td>{run.date}</td>
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
