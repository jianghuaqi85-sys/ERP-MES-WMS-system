import React, { useEffect } from 'react';
import {
  ReactFlow,
  MiniMap,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  BackgroundVariant
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';

interface TraceabilityGraphProps {
  onNodeClick: (event: React.MouseEvent, node: any) => void;
  initialNodes?: any[];
  initialEdges?: any[];
}

export const TraceabilityGraph: React.FC<TraceabilityGraphProps> = ({ 
  onNodeClick, 
  initialNodes = [], 
  initialEdges = [] 
}) => {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  // Sync props to state when they change
  useEffect(() => {
    setNodes(initialNodes);
    setEdges(initialEdges);
  }, [initialNodes, initialEdges, setNodes, setEdges]);

  return (
    <div style={{ width: '100%', height: '100%' }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeClick={onNodeClick}
        fitView
        className="bg-background"
        colorMode="dark"
      >
        <Controls className="bg-panel border border-white/10 fill-white" />
        <MiniMap 
          nodeColor={(n) => {
            if (n.id.includes('erp') || n.id.includes('product')) return '#3b82f6';
            if (n.id.includes('mes') || n.id.includes('wo')) return '#10b981';
            return '#f59e0b';
          }}
          className="bg-panel border border-white/10"
        />
        <Background variant={BackgroundVariant.Dots} gap={12} size={1} color="#334155" />
      </ReactFlow>
    </div>
  );
};
