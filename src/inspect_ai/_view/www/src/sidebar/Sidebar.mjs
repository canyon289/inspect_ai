import { html } from "htm/preact";

import { icons } from "./../Constants.mjs";
import { formatPrettyDecimal } from "./../utils/Format.mjs";

export const Sidebar = (props) => {
  const btnOffCanClass = props.offcanvas ? "" : " d-md-none";
  const sidebarOffCanClass = props.offcanvas ? " offcanvas" : " offcanvas-md";
  const logHeaders = props.logHeaders;

  return html`
    <div
      class="sidebar border-end offcanvas-start${sidebarOffCanClass}"
      id="sidebarOffCanvas"
    >
      <div
        style=${{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
        }}
      >
        <span
          style=${{
            paddingLeft: "0.5rem",
            fontWeight: "500",
            fontSize: "1.1rem",
            opacity: "0.7",
          }}
          >${props.offcanvas ? "Log History" : ""}</span
        >
        <button
          id="sidebarToggle"
          class="btn d-inline${btnOffCanClass}"
          type="button"
          data-bs-toggle="offcanvas"
          data-bs-target="#sidebarOffCanvas"
          aria-controls="sidebarOffCanvas"
          style=${{ padding: ".1rem", alignSelf: "end", width: "40px" }}
        >
          <i class=${icons.close}></i>
        </button>
      </div>
      <ul class="list-group">
        ${props.logs.files.map((file, index) => {
          const active = index === props.selected ? " active" : "";
          const time = new Date(file.mtime);
          const logHeader = logHeaders[file.name];
          const hyperparameters = logHeader
            ? {
                ...logHeader.plan?.config,
                ...logHeader.eval?.task_args,
              }
            : undefined;

          const model = logHeader?.eval?.model;
          const dataset = logHeader?.eval?.dataset;
          const scorer = logHeader?.results?.scorer?.name;

          return html`
            <li
              class="list-group-item list-group-item-action${active}"
              onclick=${() => props.onSelected(index)}
              style=${{ fontSize: "0.8rem" }}
            >
              <div
                style=${{
                  display: "flex",
                  flexDirection: "row",
                  justifyContent: "space-between",
                }}
              >
                <div style=${{ overflow: "hidden" }}>
                  <div
                    style=${{
                      fontSize: "1.5em",
                      fontWeight: "600",
                      whiteSpace: "nowrap",
                      overflow: "hidden",
                      textOverflow: "ellipsis",
                    }}
                  >
                    ${logHeader?.eval?.task || file.task}
                  </div>
                  <small class="mb-1 text-muted">
                    ${time.toDateString()}
                    ${time.toLocaleTimeString([], {
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </small>

                  ${model
                    ? html` <div>
                        <small class="mb-1 text-muted">${model}</small>
                      </div>`
                    : ""}
                </div>
                ${logHeader?.results?.metrics
                  ? html`<div
                      style=${{
                        display: "flex",
                        flexDirection: "row",
                        flexWrap: "wrap",
                        justifyContent: "flex-end",
                      }}
                    >
                      ${Object.keys(logHeader?.results.metrics).map(
                        (metric) => {
                          return html`
                            <div
                              style=${{
                                display: "flex",
                                flexDirection: "column",
                                alignItems: "center",
                                marginLeft: "1em",
                              }}
                            >
                              <div style=${{ fontWeight: 300 }}>
                                ${logHeader?.results.metrics[metric].name}
                              </div>
                              <div
                                style=${{ fontWeight: 600, fontSize: "1.5em" }}
                              >
                                ${formatPrettyDecimal(
                                  logHeader?.results.metrics[metric].value
                                )}
                              </div>
                            </div>
                          `;
                        }
                      )}
                    </div>`
                  : logHeader?.status === "error"
                  ? html`<div style=${{ color: "var(--bs-danger)" }}>
                      Eval Error
                    </div>`
                  : ""}
              </div>
              <div style=${{ marginTop: "0.4em" }}>
                <small class="mb-1 text-muted">
                  ${hyperparameters
                    ? Object.keys(hyperparameters)
                        .map((key) => {
                          return `${key}: ${hyperparameters[key]}`;
                        })
                        .join(", ")
                    : ""}
                </small>
              </div>
              ${dataset || scorer
                ? html`<div
                    style=${{
                      display: "flex",
                      justifyContent: "space-between",
                      marginTop: "0.5em",
                    }}
                  >
                    <span>dataset: ${dataset.name || "(samples)"}</span
                    ><span>scorer: ${scorer}</span>
                  </div>`
                : ""}
            </li>
          `;
        })}
      </ul>
    </div>
  `;
};
