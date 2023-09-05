import { Component, ElementRef, OnInit, OnDestroy, ViewChild, Input, OnChanges } from '@angular/core';
import { Network } from 'vis';
import { DataService } from '../services/app.data.service';
import { AppNetworkService } from '../services/app.network.service';

@Component({
  selector: 'app-network-topology',
  templateUrl: './network-topology.component.html',
  styleUrls: ['./network-topology.component.css']
})
export class NetworkTopologyComponent implements OnInit {

  @Input() stateData: any = {}; // data coming from detail panel component

  @ViewChild('treeContainer', { static: true }) treeContainer: ElementRef;

  private network: Network;

  constructor(private appNetworkService: AppNetworkService, private el: ElementRef, private dataService: DataService) { }//, private dataService: DataService) { }

  public ngOnInit(): void {

    const networkOptions: any = this.appNetworkService.getNetworkOptions()
    networkOptions["height"] = ((window.innerHeight - 160) - 48).toString()

    this.network = new Network(
      this.treeContainer.nativeElement,
      this.stateData,
      networkOptions
    );

    this.dataService.currentStateData$.subscribe((data) => {
      if (this.network !== undefined) {
        if (data !== null && data !== undefined) {
          if (typeof data == 'object') {
            if (Object.keys(data).length > 0) {
              this.network.setData(this.prepareDataForGraph(data));
              this.network.redraw()
            }
          }
        }
      }
    })

  }

  public prepareDataForGraph(data: any, showGreen: boolean = false, showRed: boolean = false, showBlue: boolean = false) {
    const networkGraph = data["network_graph"]

    const res: any = {
      "nodes": [],
      "edges": []
    }

    // Adding host nodes
    for (const node_id in networkGraph["nodes"]) {
      res["nodes"].push({ "id": networkGraph["nodes"][node_id]["id"], "label": networkGraph["nodes"][node_id]["id"] })
    }
    for (const link_id in networkGraph["links"]) {
      if (networkGraph["links"][link_id]["target"] !== networkGraph["links"][link_id]["source"]) {
        res["edges"].push({
          "from": networkGraph["links"][link_id]["source"],
          "to": networkGraph["links"][link_id]["target"],
          "id": networkGraph["links"][link_id]["source"] + "-" + networkGraph["links"][link_id]["target"]
        })
      }
    }

    const findTeam = (agent_name: string, mapping: any): string => {
      console.log(Object.keys(mapping))
      for(const team in Object.keys(mapping)) {
        console.log(team)
        if (mapping[team].includes(agent_name)) {
          return team
        }
      }
      return "None"
    }

    // Adding agents
    const team_agent_mapping: any = data["team_agent_mapping"]
    const shownTeams = [showBlue ? "blue" : "", showGreen ? "green" : "", showRed ? "red" : ""]
    for (const node of Object.keys(data["true_states"])) {
      if (node !== "success") {
        for (const session of Object.keys(data["true_states"][node]["Sessions"])) {
          const sess = data["true_states"][node]["Sessions"][session]
          const agent_name = sess["Agent"]
          const agent_team = findTeam(agent_name, team_agent_mapping).toLowerCase()
          if (agent_team !== "None") {
            if(shownTeams.includes(agent_team)) {
              res["nodes"].push({"id": agent_team + ":" + agent_name, "label": agent_name})
            }
          }
        }
      }
    }


    if(showGreen) {

    }
    
    if(showRed) {
      
    }
    
    if(showBlue) {
      
    }

    return res;
  }

  // public prepareDataForGraph() {

  //   function determineGoodOrBad(agentName: string) {
  //     if (agentName.toUpperCase().includes("DEFEND")) {
  //       return "defender"
  //     }
  //     return "attacker"
  //   }

  //   if (this.network !== undefined) {
  //     if (this.detailData !== null || undefined) {

  //       this.prepareEnvironmentForGraph()


  //       if ("nodes" in this.detailData) {
  //         for (let i = 0; i < (<Array<any>>this.detailData["nodes"]).length; i++) {
  //           if ("data" in this.detailData["nodes"][i]) {

  //             Object.assign(this.detailData["nodes"][i], {
  //               font: {
  //                 size: 30
  //               }
  //             })
  //             const accessibleNodes = this.detailData["nodes"][i]["data"]["properties"]["accessible_nodes"]

  //             for (let j = 0; j < accessibleNodes.length; j++) {
  //               const node = accessibleNodes[j]

  //               this.detailData["edges"].push({
  //                 from: this.detailData["nodes"][i]["id"],
  //                 to: node[0],
  //                 length: 0,
  //                 hidden: false,
  //                 label: "can access (" + node[1] + ")",
  //                 color: {
  //                   color: "orange"
  //                 },
  //                 smooth: {
  //                   roundness: accessibleNodes.length == 1 ? 1 : ((j * (1 / (accessibleNodes.length - 1))) - 0.5),
  //                   type: 'curvedCW'
  //                 },
  //                 arrows: {
  //                   to: {
  //                     enabled: true,
  //                     scaleFactor: 1
  //                   }
  //                 },
  //                 font: {
  //                   size: 10,
  //                   align: "middle"
  //                 },
  //                 physics: false
  //               })
  //             }

  //             let agents: any = this.detailData["nodes"][i]["data"]["properties"]["processes"]["agents"]
  //             for (const agentID in agents) {
  //               const agent = agents[agentID]

  //               if (agentID == this.lastAgentPlayed) {
  //                 this.detailData["nodes"].push({
  //                   id: agentID + "_" + this.detailData["nodes"][i]["id"],
  //                   label: agent["name"],
  //                   borderWidth: 4,
  //                   font: {
  //                     size: 12
  //                   },
  //                   color: (determineGoodOrBad(agent["name"]) == "attacker") ? {
  //                     background: "#e39090",
  //                     border: "green",
  //                     highlight: { background: "#f9b6b6", border: "#f20000" }
  //                   } : {
  //                     background: "#4decfa",
  //                     border: "green",
  //                     highlight: { background: "#e0fff7", border: "#a4d2fc" }
  //                   }
  //                 })
  //               } else {
  //                 this.detailData["nodes"].push({
  //                   id: agentID + "_" + this.detailData["nodes"][i]["id"],
  //                   label: agent["name"],
  //                   font: {
  //                     size: 12
  //                   },
  //                   color: (determineGoodOrBad(agent["name"]) == "attacker") ? {
  //                     background: "#e39090",
  //                     border: "red",
  //                     highlight: { background: "#f9b6b6", border: "#f20000" }
  //                   } : {
  //                     background: "#4decfa",
  //                     border: "blue",
  //                     highlight: { background: "#e0fff7", border: "#a4d2fc" }
  //                   }
  //                 })
  //               }
  //               this.detailData["edges"].push({
  //                 from: this.detailData["nodes"][i]["id"],
  //                 to: agentID + "_" + this.detailData["nodes"][i]["id"],
  //                 length: 0,
  //                 hidden: false,
  //                 label: "installed on",
  //                 arrows: {
  //                   from: {
  //                     enabled: true,
  //                     scaleFactor: 0.5
  //                   }
  //                 },
  //                 font: {
  //                   size: 8,
  //                   align: "middle"
  //                 },
  //                 physics: false
  //               })
  //             }

  //             if (agents.length == 0) {
  //               this.detailData["nodes"][i]["color"] = {}
  //             }
  //           }
  //         }
  //       }

  //     }
  //   }

  // }

  // public ngOnChanges(changes: any) {
  //   if (this.network !== undefined) {
  //     if (this.detailData !== null || undefined) {
  //       this.prepareDataForGraph()
  //     }
  //     this.detailData = {
  //       "nodes": [
  //         {
  //           "id": "n1",
  //           "label": "node1"
  //         },
  //         {
  //           "id": "n2",
  //           "label": "node2"
  //         }
  //       ],
  //       "edges": [{
  //         "from": "n1",
  //         "to": "n2"
  //       }]
  //     }
  //     this.network.setData(this.detailData);
  //     this.network.redraw()
  //   }
  // }

  public ngOnDestroy(): void {
    if (this.network != null) this.network.destroy();
  }

}
