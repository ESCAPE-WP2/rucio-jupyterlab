import React, { useMemo } from 'react';
import { VDomRenderer } from '@jupyterlab/apputils';
import { createUseStyles } from 'react-jss';
import { NotebookPanel } from '@jupyterlab/notebook';
import { useNotebookResolveStatusStore } from './utils/NotebookListener';
import { ResolveStatus } from './types';
import { Spinning } from './components/Spinning';

const useStyles = createUseStyles({
  main: {
    display: 'flex',
    flexDirection: 'row',
    alignItems: 'center',
    padding: '0 8px 0 8px',
    borderRadius: '4px',
    cursor: 'pointer',
    '&:hover': {
      background: 'var(--jp-layout-color2)'
    }
  },
  ready: {
    color: 'var(--jp-success-color0)'
  },
  failed: {
    color: 'var(--jp-error-color1)'
  },
  resolving: {
    color: 'var(--jp-rucio-yellow-color)'
  },
  injecting: {
    color: '#c0ca33'
  },
  rucioIcon: {
    width: '16px',
    height: '16px',
    marginRight: '4px'
  },
  statusIcon: {
    fontSize: '16px',
    marginRight: '4px'
  },
  readyIcon: {
    extend: 'statusIcon',
    color: 'var(--jp-success-color0)'
  },
  failedIcon: {
    extend: 'statusIcon',
    color: 'var(--jp-error-color1)'
  },
  resolvingIcon: {
    extend: 'statusIcon',
    color: 'var(--jp-rucio-yellow-color)'
  },
  pendingInjectionIcon: {
    extend: 'statusIcon',
    color: '#c0ca33'
  }
});

const Panel: React.FC<{ notebookPanel: NotebookPanel; onClick: { (): void } }> = ({ notebookPanel, onClick }) => {
  const classes = useStyles();
  const notebookResolveStatusStore = useNotebookResolveStatusStore();
  const notebookResolveStatus = notebookResolveStatusStore[notebookPanel.id];
  const statuses = notebookResolveStatus ? Object.keys(notebookResolveStatus).map(k => notebookResolveStatus[k]) : null;
  const computeSummarizedStatus = (statuses: ResolveStatus[]): ResolveStatus => {
    if (!statuses) {
      return null;
    } else if (statuses.length === 0) {
      return 'NOT_RESOLVED';
    } else if (statuses.includes('FAILED')) {
      return 'FAILED';
    } else if (statuses.includes('NOT_RESOLVED')) {
      return 'NOT_RESOLVED';
    } else if (statuses.includes('RESOLVING')) {
      return 'RESOLVING';
    } else if (statuses.includes('PENDING_INJECTION')) {
      return 'PENDING_INJECTION';
    } else {
      return 'READY';
    }
  };

  const summmarizedStatus = useMemo(() => computeSummarizedStatus(statuses), [notebookResolveStatus]);

  return (
    <>
      {!!summmarizedStatus && (
        <div className={classes.main} onClick={onClick}>
          <ResolverStatusIcon status={summmarizedStatus} />
          {summmarizedStatus === 'NOT_RESOLVED' && <span>Attach Variables</span>}
          {summmarizedStatus === 'FAILED' && <span className={classes.failed}>Failed to Attach</span>}
          {summmarizedStatus === 'RESOLVING' && <span className={classes.resolving}>Resolving</span>}
          {summmarizedStatus === 'PENDING_INJECTION' && <span className={classes.injecting}>Attaching</span>}
          {summmarizedStatus === 'READY' && <span className={classes.ready}>Ready</span>}
        </div>
      )}
    </>
  );
};

const ResolverStatusIcon: React.FC<{ status: ResolveStatus }> = ({ status }) => {
  const classes = useStyles();

  switch (status) {
    case 'RESOLVING':
      return <Spinning className={`${classes.resolvingIcon} material-icons`}>hourglass_top</Spinning>;
    case 'PENDING_INJECTION':
      return <Spinning className={`${classes.pendingInjectionIcon} material-icons`}>hourglass_top</Spinning>;
    case 'READY':
      return <i className={`${classes.readyIcon} material-icons`}>check_circle</i>;
    case 'FAILED':
      return <i className={`${classes.failedIcon} material-icons`}>cancel</i>;
    default:
      return <i className={`${classes.rucioIcon} jp-icon-rucio`}></i>;
  }
};

const PANEL_CLASS = 'jp-RucioExtensionInjectToolbar';

interface InjectNotebookToolbarOptions {
  notebookPanel: NotebookPanel;
  onClick: { (): void };
}
export class InjectNotebookToolbar extends VDomRenderer {
  options: InjectNotebookToolbarOptions;
  constructor(options: InjectNotebookToolbarOptions) {
    super();
    super.addClass(PANEL_CLASS);

    this.options = options;
  }

  render(): React.ReactElement {
    const { notebookPanel, onClick } = this.options;
    return <Panel notebookPanel={notebookPanel} onClick={onClick} />;
  }
}
