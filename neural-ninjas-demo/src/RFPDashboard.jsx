import React, { useState, useEffect, useRef } from 'react';
import { FileText, Search, DollarSign, CheckCircle, XCircle, AlertCircle, Loader, ChevronRight, Download, Terminal } from 'lucide-react';
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';

import AnalyticsStats from './AnalyticsStats';

const RFPProcessorSystem = () => {
    const [activeRFP, setActiveRFP] = useState(null);
    const [processing, setProcessing] = useState(false);
    const [agentLogs, setAgentLogs] = useState([]);
    const [matchedProducts, setMatchedProducts] = useState([]);
    const [finalBid, setFinalBid] = useState(null);
    const [showApproval, setShowApproval] = useState(false);
    const logsEndRef = useRef(null);

    // Data states
    const [rfpList, setRfpList] = useState([]);
    const [productCatalog, setProductCatalog] = useState([]);
    const [analyticsData, setAnalyticsData] = useState(null);

    const [uploading, setUploading] = useState(false);
    const fileInputRef = useRef(null);

    // Auto-scroll logs
    useEffect(() => {
        logsEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [agentLogs]);

    // Fetch initial data
    const fetchAllData = async () => {
        try {
            const [rfpsRes, productsRes, analyticsRes] = await Promise.all([
                fetch('http://localhost:8000/rfps'),
                fetch('http://localhost:8000/products'),
                fetch('http://localhost:8000/analytics')
            ]);

            const rfps = await rfpsRes.json();
            const products = await productsRes.json();
            const analytics = await analyticsRes.json();

            setRfpList(rfps);
            setProductCatalog(products);
            setAnalyticsData(analytics);
        } catch (error) {
            console.error("Failed to fetch data:", error);
        }
    };

    useEffect(() => {
        fetchAllData();
    }, []);

    const handleFileUpload = async (event) => {
        const file = event.target.files[0];
        if (!file) return;

        if (file.type !== 'application/pdf') {
            alert('Please upload a PDF file');
            return;
        }

        setUploading(true);
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('http://localhost:8000/upload-rfp', {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) throw new Error('Upload failed');

            const newRfp = await response.json();
            setRfpList(prev => [...prev, newRfp]);
            fetchAllData(); // Refresh analytics
            alert('RFP uploaded successfully!');
        } catch (error) {
            console.error('Error uploading RFP:', error);
            alert('Failed to upload RFP');
        } finally {
            setUploading(false);
            if (fileInputRef.current) fileInputRef.current.value = '';
        }
    };

    const processRFP = async (rfp) => {
        setActiveRFP(rfp);
        setProcessing(true);
        setAgentLogs([]);
        setMatchedProducts([]);
        setFinalBid(null);
        setShowApproval(false);

        try {
            const response = await fetch('http://localhost:8000/process-rfp', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ rfp_id: rfp.rfp_id || rfp.id }) // Handle both cases just in case
            });

            const data = await response.json();

            // Simulate streaming logs for effect
            for (const log of data.logs) {
                setAgentLogs(prev => [...prev, log]);
                await new Promise(r => setTimeout(r, 100)); // 100ms delay between logs
            }

            if (data.success && data.bid) {
                setFinalBid(data.bid);
                setMatchedProducts([data.bid.product]); // Show the selected product
                setShowApproval(true);
                fetchAllData(); // Refresh analytics
            }

        } catch (error) {
            console.error("Error processing RFP:", error);
            setAgentLogs(prev => [...prev, {
                agent: "System",
                message: "Error communicating with backend server.",
                timestamp: new Date().toLocaleTimeString()
            }]);
        } finally {
            setProcessing(false);
        }
    };

    const updateStatus = async (status) => {
        const activeId = activeRFP.rfp_id || activeRFP.id;
        try {
            const response = await fetch(`http://localhost:8000/rfps/${activeId}/status`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ status })
            });

            if (!response.ok) throw new Error('Failed to update status');

            // Optimistic update
            const updatedRFPs = rfpList.map(rfp => {
                const currentId = rfp.rfp_id || rfp.id;
                return currentId === activeId ? { ...rfp, status } : rfp;
            });
            setRfpList(updatedRFPs);

            // Refresh all data to ensure consistency
            fetchAllData();
            return true;
        } catch (error) {
            console.error("Error updating status:", error);
            alert("Failed to update status on server");
            return false;
        }
    };

    const approveBid = async () => {
        const success = await updateStatus('approved');
        if (success) {
            alert(`Bid approved! Generating final PDF document...`);
        }
    };

    const rejectBid = async () => {
        const success = await updateStatus('rejected');
        if (success) {
            alert(`Bid rejected. Sending for manual review...`);
        }
    };

    const generatePDF = () => {
        if (!finalBid) return;

        const doc = new jsPDF();
        const primaryColor = [15, 23, 42]; // Slate 900
        const accentColor = [34, 197, 94]; // Green 500

        // -- Header --
        doc.setFillColor(...primaryColor);
        doc.rect(0, 0, 210, 40, 'F');

        doc.setTextColor(255, 255, 255);
        doc.setFontSize(22);
        doc.setFont('helvetica', 'bold');
        doc.text("NEURAL NINJAS", 20, 20);

        doc.setFontSize(12);
        doc.setFont('helvetica', 'normal');
        doc.text("AI-Powered Bid Proposal", 20, 30);

        doc.text(`Date: ${new Date().toLocaleDateString()}`, 150, 20);
        doc.text(`Ref: ${finalBid.rfp_id}`, 150, 30);

        let yPos = 55;

        // -- Executive Summary --
        doc.setTextColor(0, 0, 0);
        doc.setFontSize(16);
        doc.setFont('helvetica', 'bold');
        doc.text("Executive Summary", 20, yPos);
        yPos += 10;

        doc.setFontSize(10);
        doc.setFont('helvetica', 'normal');
        doc.setTextColor(60, 60, 60);

        const clientText = `Prepared for: ${finalBid.client}`;
        doc.text(clientText, 20, yPos);
        yPos += 8;

        const summaryText = `Based on your requirements for ${finalBid.quantity} liters, we have identified an optimal solution from our catalog that meets all technical specifications including: ${finalBid.product.specs}.`;
        const splitSummary = doc.splitTextToSize(summaryText, 170);
        doc.text(splitSummary, 20, yPos);
        yPos += splitSummary.length * 6 + 10;

        // -- Product Solution --
        doc.setFontSize(16);
        doc.setFont('helvetica', 'bold');
        doc.setTextColor(0, 0, 0);
        doc.text("Proposed Solution", 20, yPos);
        yPos += 10;

        autoTable(doc, {
            startY: yPos,
            head: [['Specification', 'Details']],
            body: [
                ['Product Name', finalBid.product.name],
                ['SKU', finalBid.product.sku],
                ['Technical Specs', finalBid.product.specs],
                ['Stock Availability', `${finalBid.product.stock} Liters (Immediate)`],
                ['Confidence Match', `${finalBid.confidence}%`]
            ],
            theme: 'grid',
            headStyles: { fillColor: primaryColor, textColor: 255 },
            styles: { fontSize: 10, cellPadding: 4 },
            columnStyles: { 0: { fontStyle: 'bold', width: 50 } }
        });

        yPos = doc.lastAutoTable.finalY + 20;

        // -- Pricing Breakdown --
        doc.setFontSize(16);
        doc.setFont('helvetica', 'bold');
        doc.setTextColor(0, 0, 0);
        doc.text("Commercial Proposal", 20, yPos);
        yPos += 10;

        autoTable(doc, {
            startY: yPos,
            head: [['Item', 'Rate', 'Quantity', 'Total']],
            body: [
                [
                    finalBid.product.name,
                    `$${finalBid.pricing.unit_price.toFixed(2)} / L`,
                    `${finalBid.quantity} L`,
                    `$${finalBid.pricing.base_price.toFixed(2)}`
                ],
                [
                    `Volume Discount (${finalBid.pricing.discount}%)`,
                    '',
                    '',
                    `-$${finalBid.pricing.discount_amount.toFixed(2)}`
                ],
                [
                    { content: 'Grand Total', styles: { fontStyle: 'bold', fillColor: [240, 253, 244] } },
                    '',
                    '',
                    { content: `$${finalBid.pricing.total.toFixed(2)}`, styles: { fontStyle: 'bold', textColor: accentColor } }
                ]
            ],
            theme: 'striped',
            headStyles: { fillColor: primaryColor, textColor: 255 },
            styles: { fontSize: 10, cellPadding: 4 },
            footStyles: { fillColor: [241, 245, 249] }
        });

        // -- Footer --
        const pageHeight = doc.internal.pageSize.height;
        doc.setFontSize(8);
        doc.setTextColor(150, 150, 150);
        doc.text("Generated by Neural Ninjas AI Agent System | EY Techathon 5.0", 105, pageHeight - 10, { align: 'center' });

        doc.save(`Bid_Proposal_${finalBid.rfp_id}.pdf`);
    };

    return (
        <div className="min-h-screen bg-[#0f172a] text-slate-200 p-6 font-sans">
            <div className="max-w-7xl mx-auto space-y-6">

                {/* Header */}
                <div className="bg-[#1e293b] border border-slate-700/50 rounded-xl p-6 shadow-lg flex justify-between items-center">
                    <div>
                        <h1 className="text-3xl font-bold text-white mb-1">AI-Powered RFP Processing System</h1>
                        <p className="text-slate-400">Multi-Agent System for Industrial Manufacturing Bids</p>
                    </div>
                    <div>
                        <input
                            type="file"
                            ref={fileInputRef}
                            onChange={handleFileUpload}
                            accept=".pdf"
                            className="hidden"
                        />
                        <button
                            onClick={() => fileInputRef.current?.click()}
                            disabled={uploading}
                            className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-lg flex items-center gap-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {uploading ? <Loader className="w-4 h-4 animate-spin" /> : <FileText className="w-4 h-4" />}
                            Upload RFP (PDF)
                        </button>
                    </div>
                </div>

                {/* Analytics Dashboard */}
                <AnalyticsStats stats={analyticsData} />

                {/* Incoming RFPs */}
                <div className="bg-[#1e293b] border border-slate-700/50 rounded-xl p-6 shadow-lg">
                    <div className="flex items-center gap-2 mb-4">
                        <FileText className="w-5 h-5 text-slate-300" />
                        <h2 className="text-xl font-bold text-white">Incoming RFPs</h2>
                    </div>
                    <div className="space-y-3">
                        {rfpList.map(rfp => (
                            <div
                                key={rfp.rfp_id || rfp.id}
                                onClick={() => !processing && processRFP(rfp)}
                                className={`p-4 rounded-lg border transition-all cursor-pointer glass-shine ${(activeRFP?.rfp_id === rfp.rfp_id || activeRFP?.id === rfp.id)
                                    ? 'bg-blue-900/20 border-blue-500/50'
                                    : 'bg-[#334155]/30 border-slate-700 hover:bg-[#334155]/50'
                                    }`}
                            >
                                <div className="flex justify-between items-start mb-2">
                                    <div>
                                        <span className="text-white font-bold block">{rfp.rfp_id || rfp.id}</span>
                                        <span className="text-slate-300 text-sm">{rfp.client}</span>
                                    </div>
                                    <span className={`text-xs px-2 py-1 rounded border ${rfp.status === 'approved'
                                        ? 'bg-green-900/50 text-green-400 border-green-500/30'
                                        : rfp.status === 'rejected'
                                            ? 'bg-red-900/50 text-red-400 border-red-500/30'
                                            : 'bg-[#422006] text-[#facc15] border-[#facc15]/20'
                                        }`}>
                                        {rfp.status}
                                    </span>
                                </div>
                                <p className="text-slate-400 text-sm">{rfp.content}</p>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Live Agent Activity */}
                <div className="bg-[#1e293b] border border-slate-700/50 rounded-xl p-6 shadow-lg">
                    <div className="flex items-center gap-2 mb-4">
                        <AlertCircle className="w-5 h-5 text-slate-300" />
                        <h2 className="text-xl font-bold text-white">Live Agent Activity</h2>
                    </div>
                    <div className="bg-[#0f172a] rounded-lg p-4 h-64 overflow-y-auto font-mono text-sm border border-slate-700/50">
                        {agentLogs.length === 0 ? (
                            <div className="text-slate-500 text-center mt-20">Select an RFP to start processing...</div>
                        ) : (
                            <div className="space-y-1.5">
                                {agentLogs.map((log, idx) => (
                                    <div key={idx} className="flex gap-3">
                                        <span className="text-blue-400 shrink-0">{log.timestamp}</span>
                                        <div className="flex gap-2">
                                            <span className={`font-bold shrink-0 ${log.agent === 'Sales Agent' ? 'text-purple-400' :
                                                log.agent === 'Technical Agent' ? 'text-green-400' :
                                                    log.agent === 'Pricing Agent' ? 'text-yellow-400' : 'text-blue-400'
                                                }`}>
                                                [{log.agent}]:
                                            </span>
                                            <span className="text-slate-300">{log.message}</span>
                                        </div>
                                    </div>
                                ))}
                                <div ref={logsEndRef} />
                            </div>
                        )}
                    </div>
                </div>

                {/* Matched Products */}
                {matchedProducts.length > 0 && (
                    <div className="bg-[#1e293b] border border-slate-700/50 rounded-xl p-6 shadow-lg">
                        <div className="flex items-center gap-2 mb-4">
                            <Search className="w-5 h-5 text-slate-300" />
                            <h2 className="text-xl font-bold text-white">Matched Products</h2>
                        </div>
                        {matchedProducts.map((product, idx) => (
                            <div key={idx} className="bg-[#334155]/30 border border-slate-700 rounded-lg p-4 flex justify-between items-center">
                                <div>
                                    <div className="flex items-center gap-2">
                                        <span className="text-white font-bold text-lg">{product.name}</span>
                                        <span className="text-slate-400 text-sm">({product.sku})</span>
                                    </div>
                                    <p className="text-slate-400 text-sm mt-1">{product.specs}</p>
                                    <div className="text-green-400 font-bold mt-2">${product.price}/liter</div>
                                </div>
                                <div className="text-right">
                                    {/* Confidence score is not in product dict from API unless we add it, but for now we just show the product */}
                                    <div className="text-slate-400 text-sm mt-2">Stock: {product.stock}L</div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}

                {/* Generated Bid */}
                {showApproval && finalBid && (
                    <div className="bg-[#1e293b] border border-slate-700/50 rounded-xl p-6 shadow-lg">
                        <div className="flex items-center gap-2 mb-4">
                            <DollarSign className="w-5 h-5 text-slate-300" />
                            <h2 className="text-xl font-bold text-white">Generated Bid - Awaiting Approval</h2>
                        </div>

                        <div className="bg-[#2d2a4a]/30 border border-purple-500/30 rounded-xl overflow-hidden">
                            <div className="p-6 grid grid-cols-2 gap-y-6 gap-x-12">
                                <div>
                                    <div className="text-slate-400 text-sm mb-1">RFP ID</div>
                                    <div className="text-white font-bold text-lg">{finalBid.rfp_id}</div>
                                </div>
                                <div>
                                    <div className="text-slate-400 text-sm mb-1">Client</div>
                                    <div className="text-white font-bold text-lg">{finalBid.client}</div>
                                </div>
                                <div>
                                    <div className="text-slate-400 text-sm mb-1">Product</div>
                                    <div className="text-white font-bold text-lg">{finalBid.product.name}</div>
                                </div>
                                <div>
                                    <div className="text-slate-400 text-sm mb-1">Quantity</div>
                                    <div className="text-white font-bold text-lg">{finalBid.quantity} liters</div>
                                </div>
                            </div>

                            <div className="border-t border-slate-700/50 p-6 bg-[#1e293b]/50">
                                <div className="flex justify-between items-center mb-2">
                                    <span className="text-slate-400">Base Price:</span>
                                    <span className="text-white font-mono">${finalBid.pricing.base_price.toFixed(2)}</span>
                                </div>
                                {finalBid.pricing.discount > 0 && (
                                    <div className="flex justify-between items-center mb-4">
                                        <span className="text-green-400">Volume Discount ({finalBid.pricing.discount}%):</span>
                                        <span className="text-green-400 font-mono">-${finalBid.pricing.discount_amount.toFixed(2)}</span>
                                    </div>
                                )}
                                <div className="flex justify-between items-center pt-4 border-t border-slate-700/50">
                                    <span className="text-white text-xl font-bold">Total Bid:</span>
                                    <span className="text-green-400 text-2xl font-bold font-mono">${finalBid.pricing.total.toFixed(2)}</span>
                                </div>
                            </div>

                            <div className="p-4 bg-[#1e293b] flex gap-4">
                                <button
                                    onClick={approveBid}
                                    className="flex-1 bg-green-600 hover:bg-green-700 text-white font-bold py-3 rounded-lg flex items-center justify-center gap-2 transition-colors">
                                    <CheckCircle className="w-5 h-5" />
                                    Approve Bid
                                </button>
                                <button
                                    onClick={rejectBid}
                                    className="flex-1 bg-red-500 hover:bg-red-600 text-white font-bold py-3 rounded-lg flex items-center justify-center gap-2 transition-colors">
                                    <XCircle className="w-5 h-5" />
                                    Reject
                                </button>
                                <button
                                    onClick={generatePDF}
                                    className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-lg flex items-center justify-center gap-2 transition-colors">
                                    <Download className="w-5 h-5" />
                                    PDF
                                </button>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default RFPProcessorSystem;