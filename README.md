# Applied AI Capstone Project
By Kwok Shi Ming Jasmine, Supervised by Dr. Adela Lau <br />
May, 2024

## Abstract
The evolving landscape of global education demands innovative solutions to address the 
challenges of curriculum rigidity and the disconnect between educational output and market 
needs. This study explores the potential of blockchain technology as a transformative tool for the 
educational sector. By integrating decentralized and centralized blockchain architectures, we 
propose a novel educational model that utilizes Ethereum-based Non-Fungible Tokens (NFTs) 
and AI-driven predictive analytics to enhance curriculum flexibility and personalization. <br />

Our approach involves the development of a dual blockchain system where a decentralized 
platform facilitates the creation, transaction, and verification of educational content as NFTs, 
ensuring the security and authenticity of materials. Concurrently, a centralized blockchain 
supports dynamic curriculum adjustments and real-time educational tracking, enhanced by AI 
capabilities that predict learning outcomes based on student interaction data. This integrated 
system not only safeguards intellectual property but also fosters a responsive and adaptive 
educational environment. The findings suggest that blockchain technology can potentially 
revolutionize educational practices by providing a more personalized, secure, and efficient 
learning experience. <br />

[Report](Report.pdf) <br />
[Presentation Slides](Presentation.pdf) <br />
[Demo Video](Demo.mp4) <br />

## Development Environment Specifications
Python 3.11.4 <br />
go-ipfs version: 0.7.0 <br />
Repo version: 10 <br />
System version: amd64/windows <br />
Golang version: go1.14.4 <br />

## Execution Steps
> cd go-ipfs_v0.7.0/go-ipfs
> 
> ipfs daemon
>
> python BlockchainAPI.py
>
> python NFTMarketplaceAPI.py
>
> python NFTMarketplaceClient.py
