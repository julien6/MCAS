import { Component, ElementRef, OnInit, OnDestroy, ViewChild, Input, OnChanges } from '@angular/core';
import { Network } from 'vis';
import { AppNetworkService } from '../services/app.network.service';

@Component({
  selector: 'app-network-topology',
  templateUrl: './network-topology.component.html',
  styleUrls: ['./network-topology.component.css']
})
export class NetworkTopologyComponent implements OnInit {

  @ViewChild('treeContainer', { static: true }) treeContainer: ElementRef;

  @Input() detailData: any = {}; // data coming from detail panel component
  @Input() lastAgentPlayed: string = ""; // data coming from detail panel component
  private network: Network;

  constructor(private appNetworkService: AppNetworkService) { }//, private worldStateService: WorldStateService) { }

  public ngOnInit(): void {

    // this.worldStateService.currentNetworkGraph$.subscribe((data) => {
    //   this.detailData = data
    // })

    this.network = new Network(
      this.treeContainer.nativeElement,
      this.detailData,
      this.appNetworkService.getNetworkOptions()
    );

  }

  public prepareEnvironmentForGraph() {
    const res: any = {
      "nodes": [],
      "edges": []
    }
    const nodeNames = Object.keys(this.detailData)
    for (const node in nodeNames) {
      res["nodes"].push({ "label": nodeNames[node], "id": nodeNames[node], "data": this.detailData[nodeNames[node]] })
    }
    this.detailData = res
  }

  public prepareDataForGraph() {

    function determineGoodOrBad(agentName: string) {
      if (agentName.toUpperCase().includes("DEFEND")) {
        return "defender"
      }
      return "attacker"
    }

    if (this.network !== undefined) {
      if (this.detailData !== null || undefined) {

        this.prepareEnvironmentForGraph()


        if ("nodes" in this.detailData) {
          for (let i = 0; i < (<Array<any>>this.detailData["nodes"]).length; i++) {
            if ("data" in this.detailData["nodes"][i]) {

              Object.assign(this.detailData["nodes"][i], {
                font: {
                  size: 30
                }
              })
              const accessibleNodes = this.detailData["nodes"][i]["data"]["properties"]["accessible_nodes"]

              for (let j = 0; j < accessibleNodes.length; j++) {
                const node = accessibleNodes[j]

                this.detailData["edges"].push({
                  from: this.detailData["nodes"][i]["id"],
                  to: node[0],
                  length: 0,
                  hidden: false,
                  label: "can access (" + node[1] + ")",
                  color: {
                    color: "orange"
                  },
                  smooth: {
                    roundness: accessibleNodes.length == 1 ? 1 : ((j * (1 / (accessibleNodes.length - 1))) - 0.5),
                    type: 'curvedCW'
                  },
                  arrows: {
                    to: {
                      enabled: true,
                      scaleFactor: 1
                    }
                  },
                  font: {
                    size: 10,
                    align: "middle"
                  },
                  physics: false
                })
              }

              let agents: any = this.detailData["nodes"][i]["data"]["properties"]["processes"]["agents"]
              for (const agentID in agents) {
                const agent = agents[agentID]

                if (agentID == this.lastAgentPlayed) {
                  this.detailData["nodes"].push({
                    id: agentID + "_" + this.detailData["nodes"][i]["id"],
                    label: agent["name"],
                    borderWidth: 4,
                    font: {
                      size: 12
                    },
                    color: (determineGoodOrBad(agent["name"]) == "attacker") ? {
                      background: "#e39090",
                      border: "green",
                      highlight: { background: "#f9b6b6", border: "#f20000" }
                    } : {
                      background: "#4decfa",
                      border: "green",
                      highlight: { background: "#e0fff7", border: "#a4d2fc" }
                    }
                  })
                } else {
                  this.detailData["nodes"].push({
                    id: agentID + "_" + this.detailData["nodes"][i]["id"],
                    label: agent["name"],
                    font: {
                      size: 12
                    },
                    color: (determineGoodOrBad(agent["name"]) == "attacker") ? {
                      background: "#e39090",
                      border: "red",
                      highlight: { background: "#f9b6b6", border: "#f20000" }
                    } : {
                      background: "#4decfa",
                      border: "blue",
                      highlight: { background: "#e0fff7", border: "#a4d2fc" }
                    }
                  })
                }
                this.detailData["edges"].push({
                  from: this.detailData["nodes"][i]["id"],
                  to: agentID + "_" + this.detailData["nodes"][i]["id"],
                  length: 0,
                  hidden: false,
                  label: "installed on",
                  arrows: {
                    from: {
                      enabled: true,
                      scaleFactor: 0.5
                    }
                  },
                  font: {
                    size: 8,
                    align: "middle"
                  },
                  physics: false
                })
              }

              if (agents.length == 0) {
                this.detailData["nodes"][i]["color"] = {}
              }
            }
          }
        }

      }
    }

  }

  public ngOnChanges(changes: any) {
    if (this.network !== undefined) {
      // if (this.detailData !== null || undefined) {
      //   this.prepareDataForGraph()
      // }
      this.detailData = {
        "nodes": [
          {
            "id": "n1",
            "label": "node1"
          },
          {
            "id": "n2",
            "label": "node2"
          }
        ],
        "edges": [{
          "from": "n1",
          "to": "n2"
        }]
      }
      this.network.setData(this.detailData);
      this.network.redraw()
    }
  }

  public ngOnDestroy(): void {
    if (this.network != null) this.network.destroy();
  }

}
